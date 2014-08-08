DROP TYPE IF EXISTS xbusevent_type_servicecount CASCADE;
DROP TYPE IF EXISTS xbusevent_type_zmqids CASCADE;
DROP TYPE IF EXISTS xbusevent_type_event_tree CASCADE;

CREATE TYPE xbusevent_type_servicecount AS (id integer, name character varying, consumer boolean, count integer);
CREATE TYPE xbusevent_type_zmqids AS (service_id integer, consumer boolean, zmqids integer[], role_ids integer[]);
CREATE TYPE xbusevent_type_event_tree AS (id integer, service_id integer, start boolean, child_ids integer[]);

CREATE OR REPLACE FUNCTION xbusrole_sign_in(param_login character varying, param_zmqid integer) RETURNS character varying AS
$BODY$
DECLARE
	v_role_id integer;
BEGIN
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	LOCK role_active IN EXCLUSIVE MODE;
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
	v_role_id integer;
BEGIN
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	LOCK role_active IN EXCLUSIVE MODE;
	IF (SELECT count(*) FROM role_active where role_active.role_id = v_role_id) > 0 THEN
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
	v_role_id integer;
BEGIN
	SELECT INTO v_role_id id FROM role WHERE role.login = param_login;
	IF v_role_id IS NULL THEN RETURN 'err_login';
	END IF;
	LOCK role_active IN EXCLUSIVE MODE;
	IF (SELECT zmqid FROM role_active where role_active.role_id = v_role_id) = param_zmqid THEN
		UPDATE role_active SET ready = true WHERE role_active.role_id = v_role_id;
		RETURN 'ack_ready';
	ELSE
		RETURN 'err_ready';
	END IF;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusrole_reset() RETURNS void AS
$BODY$
BEGIN
	DELETE FROM role_active
	WHERE role_id IN (
		SELECT role_active.role_id FROM role_active
		JOIN role ON role_active.role_id = role.id
		JOIN service ON role.service_id = service.id
		WHERE NOT service.consumer
	);
	UPDATE role_active SET zmqid = NULL, ready = false;
END;
$BODY$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION xbusevent_get_services(param_event_type character varying) RETURNS SETOF xbusevent_type_zmqids AS
$BODY$
DECLARE
	sc xbusevent_type_servicecount;
	zmq xbusevent_type_zmqids;
	v_role_ids integer[];
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

