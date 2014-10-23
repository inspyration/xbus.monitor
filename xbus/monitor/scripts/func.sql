DROP TYPE IF EXISTS xbusevent_type_servicecount CASCADE;
DROP TYPE IF EXISTS xbusevent_type_zmqids CASCADE;
DROP TYPE IF EXISTS xbusevent_type_event_tree CASCADE;

CREATE TYPE xbusevent_type_servicecount AS (id uuid, name character varying, consumer boolean, count integer);
CREATE TYPE xbusevent_type_zmqids AS (service_id uuid, consumer boolean, zmqids integer[], role_ids uuid[]);
CREATE TYPE xbusevent_type_event_tree AS (id uuid, service_id uuid, start boolean, child_ids uuid[]);

CREATE OR REPLACE FUNCTION xbusrole_sign_in(param_login character varying, param_zmqid integer) RETURNS character varying AS
$BODY$
DECLARE
	v_role_id uuid;
BEGIN
	LOCK role_active IN EXCLUSIVE MODE;
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	UPDATE role SET last_logged = localtimestamp where id = v_role_id;
	IF (SELECT count(*) FROM role_active where role_active.role_id = v_role_id) > 0 THEN
		UPDATE role_active SET zmqid = param_zmqid, ready = true, last_act_date = localtimestamp WHERE role_active.role_id = v_role_id;
	ELSE
		INSERT INTO role_active (role_id, zmqid, ready, last_act_date) values (v_role_id, param_zmqid, true, localtimestamp);
	END IF;
	RETURN 'ack_sign_in';
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusrole_sign_out(param_login character varying, param_zmqid integer) RETURNS character varying AS
$BODY$
DECLARE
	v_role_id uuid;
BEGIN
	LOCK role_active IN EXCLUSIVE MODE;
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	IF (SELECT zmqid FROM role_active where role_active.role_id = v_role_id) = param_zmqid THEN
		DELETE FROM role_active WHERE role_active.role_id = v_role_id;
		RETURN 'ack_sign_out';
	END IF;
	RETURN 'err_sign_out';
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusrole_ready(param_login character varying, param_zmqid integer) RETURNS character varying AS
$BODY$
DECLARE
	v_role_id uuid;
BEGIN
	LOCK role_active IN EXCLUSIVE MODE;
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	IF (SELECT zmqid FROM role_active where role_active.role_id = v_role_id) = param_zmqid THEN
		UPDATE role_active SET ready = true WHERE role_active.role_id = v_role_id;
		RETURN 'ack_ready';
	ELSE
		RETURN 'err_ready';
	END IF;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusrole_unavailable(param_login character varying, param_zmqid integer) RETURNS character varying AS
$BODY$
DECLARE
	v_role_id uuid;
BEGIN
	LOCK role_active IN EXCLUSIVE MODE;
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	IF (SELECT zmqid FROM role_active where role_active.role_id = v_role_id) = param_zmqid THEN
		UPDATE role_active SET ready = false WHERE role_active.role_id = v_role_id;
		RETURN 'ack_unavailable';
	ELSE
		RETURN 'err_unavailable';
	END IF;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusbroker_reset() RETURNS void AS
$BODY$
BEGIN
	LOCK role_active IN EXCLUSIVE MODE;
	LOCK envelope IN EXCLUSIVE MODE;
	DELETE FROM role_active
	WHERE role_id IN (
		SELECT role_active.role_id FROM role_active
		JOIN role ON role_active.role_id = role.id
		JOIN service ON role.service_id = service.id
		WHERE NOT service.consumer
	);
	UPDATE role_active SET zmqid = NULL, ready = false;
	UPDATE envelope SET state = 'canc' WHERE state = 'emit';
	UPDATE envelope SET state = 'stop' WHERE state = 'exec';
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusevent_get_services(param_event_type character varying) RETURNS SETOF xbusevent_type_zmqids AS
$BODY$
DECLARE
	sc xbusevent_type_servicecount;
	zmq xbusevent_type_zmqids;
	v_role_ids uuid[];
BEGIN
	LOCK role_active IN EXCLUSIVE MODE;
	FOR sc IN SELECT service.id, service.name, service.consumer, count(*)
	FROM event_node
	JOIN event_type ON event_type.id = event_node.type_id
	LEFT JOIN service ON service.id = event_node.service_id
	WHERE event_type.name = param_event_type
	GROUP BY service.id, event_type.id
	LOOP
		IF sc.consumer THEN
			SELECT sz.service_id, bool_and(sz.ready), array_agg(sz.zmqid), array_agg(sz.id) INTO zmq
			FROM (
				SELECT role.id, role_active.ready, role.service_id, role_active.zmqid
				FROM role_active
				LEFT JOIN role ON role.service_id = sc.id
				WHERE role.id = role_active.role_id
			) as sz
			GROUP BY sz.service_id;
			IF NOT zmq.consumer THEN
				RAISE EXCEPTION 'Some consumers are unavailable for service %%', sc.name;
			END IF;
			IF zmq.service_id IS NULL THEN
				SELECT sc.id, true, '{}', '{}' INTO zmq;
			END IF;
			RETURN NEXT zmq;
		ELSE
			SELECT sz.service_id, false, array_agg(sz.zmqid), array_agg(sz.id) INTO zmq
			FROM (
				SELECT role.id, role.service_id, role_active.zmqid
				FROM role_active
				LEFT JOIN role ON role.service_id = sc.id
				WHERE role_active.ready = TRUE AND role.id = role_active.role_id
				LIMIT sc.count
			) as sz
			GROUP BY sz.service_id;
			IF array_length(zmq.zmqids, 1) = sc.count THEN
				v_role_ids := array_cat(v_role_ids, zmq.role_ids);
				RETURN NEXT zmq;
			ELSE
				RAISE EXCEPTION 'Not enough providers available for service %%', sc.name;
			END IF;
		END IF;
	END LOOP;
	UPDATE role_active
	SET ready = false
	WHERE role_id = ANY(v_role_ids);
	RETURN;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusevent_get_event_tree(param_event_type character varying) RETURNS SETOF xbusevent_type_event_tree AS
$BODY$
BEGIN
	RETURN QUERY SELECT event_node.id, event_node.service_id, event_node.start, array_remove(array_agg(children.child_id), NULL) as child_ids
	FROM event_node
	JOIN event_type ON event_type.id = event_node.type_id
	LEFT JOIN event_node_rel AS children ON event_node.id = children.parent_id
	WHERE event_type.name = param_event_type
	GROUP BY event_node.id
	ORDER BY start desc;
	RETURN;
END
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusenvelope_new_envelope(param_login character varying, param_env_uuid uuid) RETURNS uuid AS
$BODY$
DECLARE
	v_emitter_id uuid;
BEGIN
	LOCK emitter IN EXCLUSIVE MODE;
	SELECT INTO v_emitter_id id FROM emitter WHERE emitter.login = param_login;
	IF v_emitter_id IS NULL THEN RAISE EXCEPTION 'Invalid emitter login: %%', param_login;
	END IF;
	UPDATE emitter SET last_emit = localtimestamp where emitter.id = v_emitter_id;
    INSERT INTO envelope (id, emitter_id, state, posted_date) VALUES (param_env_uuid, v_emitter_id, 'emit', localtimestamp);
    RETURN v_emitter_id;
END
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusenvelope_new_event(param_evt_type character varying, param_emitter_id uuid, param_env_uuid uuid, param_evt_uuid uuid, param_estimate int) RETURNS void AS
$BODY$
DECLARE
	v_event_type_id uuid;
BEGIN
	SELECT INTO v_event_type_id event_type.id
	FROM emitter
	JOIN emitter_profile_event_type_rel ON emitter.profile_id = emitter_profile_event_type_rel.profile_id
	JOIN event_type ON emitter_profile_event_type_rel.event_id = event_type.id
	WHERE emitter.id = param_emitter_id AND event_type.name = param_evt_type;
	IF v_event_type_id IS NULL THEN RAISE EXCEPTION 'Login %% is not allowed to post event of type %%', param_emitter_id, param_evt_type;
	END IF;
    INSERT INTO event (id, envelope_id, type_id, emitter_id, estimated_items, started_date) VALUES (param_evt_uuid, param_env_uuid, v_event_type_id, param_emitter_id, param_estimate, localtimestamp);
    RETURN;
END
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusenvelope_fail(param_env_uuid uuid, param_evt_uuid uuid, param_service_id uuid, param_items text, param_message text) RETURNS void AS
$BODY$
BEGIN
	LOCK envelope IN EXCLUSIVE MODE;
	UPDATE envelope SET state = 'fail' WHERE id = param_env_uuid;
	INSERT INTO event_error (id, envelope_id, event_id, service_id, items, message, error_date) VALUES (uuid_generate_v4(), param_env_uuid, param_evt_uuid, param_service_id, param_items, param_message, localtimestamp);
	RETURN;
END
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusenvelope_cancel(param_env_uuid uuid, param_evt_uuid uuid, param_message text) RETURNS void AS
$BODY$
BEGIN
	LOCK envelope IN EXCLUSIVE MODE;
	UPDATE envelope SET state = 'canc' WHERE id = param_env_uuid;
	INSERT INTO event_error (id, envelope_id, event_id, message, error_date) VALUES (uuid_generate_v4(), param_env_uuid, param_evt_uuid, param_message, localtimestamp);
	RETURN;
END
$BODY$
LANGUAGE plpgsql;

