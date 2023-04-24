--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2 (Debian 13.2-1.pgdg100+1)
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS motivation;
--
-- Name: motivation; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE motivation WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE motivation OWNER TO postgres;

\connect motivation

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    activity_id integer NOT NULL,
    name text NOT NULL,
    lesson_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activities_id_seq OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.activity_id;


--
-- Name: activity_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_records (
    record_id integer NOT NULL,
    teacher_id integer NOT NULL,
    activity_id integer NOT NULL,
    hours numeric(5,2),
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activity_records OWNER TO postgres;

--
-- Name: activity_records_record_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_records_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activity_records_record_id_seq OWNER TO postgres;

--
-- Name: activity_records_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_records_record_id_seq OWNED BY public.activity_records.record_id;


--
-- Name: course_join_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.course_join_codes (
    code_id character varying(12) NOT NULL,
    course_id integer,
    comment text,
    activated_by_teacher_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.course_join_codes OWNER TO postgres;

--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courses (
    course_id integer NOT NULL,
    name text NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.courses_id_seq OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.course_id;


--
-- Name: excel_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.excel_reports (
    report_id integer NOT NULL,
    file_data bytea,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.excel_reports OWNER TO postgres;

--
-- Name: excel_reports_report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.excel_reports_report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.excel_reports_report_id_seq OWNER TO postgres;

--
-- Name: excel_reports_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.excel_reports_report_id_seq OWNED BY public.excel_reports.report_id;


--
-- Name: lessons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lessons (
    lesson_id integer NOT NULL,
    date_from timestamp with time zone NOT NULL,
    topic text,
    course_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    date_to timestamp with time zone
);


ALTER TABLE public.lessons OWNER TO postgres;

--
-- Name: lessons_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lessons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lessons_id_seq OWNER TO postgres;

--
-- Name: lessons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lessons_id_seq OWNED BY public.lessons.lesson_id;


--
-- Name: teacher_courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_courses (
    teacher_id integer,
    course_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.teacher_courses OWNER TO postgres;

--
-- Name: teachers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers (
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    teacher_id integer NOT NULL,
    is_manager boolean DEFAULT false
);


ALTER TABLE public.teachers OWNER TO postgres;

--
-- Name: activities activity_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN activity_id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- Name: activity_records record_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records ALTER COLUMN record_id SET DEFAULT nextval('public.activity_records_record_id_seq'::regclass);


--
-- Name: courses course_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses ALTER COLUMN course_id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: excel_reports report_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.excel_reports ALTER COLUMN report_id SET DEFAULT nextval('public.excel_reports_report_id_seq'::regclass);


--
-- Name: lessons lesson_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons ALTER COLUMN lesson_id SET DEFAULT nextval('public.lessons_id_seq'::regclass);


--
-- Data for Name: activities; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (19, 'Подготовка презентации', 26, '2023-04-22 21:12:26.143132');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (20, 'Запись видео', 26, '2023-04-22 21:12:33.026085');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (21, 'Подготовка теста', 26, '2023-04-22 21:12:39.133995');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (22, 'Подготовка презентации', 27, '2023-04-22 21:13:20.29119');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (23, 'Проверка домашнего задания', 27, '2023-04-22 21:13:26.885123');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (24, 'Запись видео', 27, '2023-04-22 21:13:32.697543');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (25, 'Подготовка презентации', 28, '2023-04-22 21:14:05.983043');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (26, 'Запись видео', 28, '2023-04-22 21:14:12.593071');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (27, 'Подготовка презентации', 29, '2023-04-22 21:14:38.79313');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (28, 'Проверка домашнего задания', 29, '2023-04-22 21:14:44.145714');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (29, 'Подготовка теста', 29, '2023-04-22 21:14:51.02215');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (30, 'Подготовка презентации', 30, '2023-04-22 21:15:33.016538');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (31, 'Запись видео', 30, '2023-04-22 21:15:38.492485');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (32, 'Подготовка теста', 30, '2023-04-22 21:15:46.208443');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (33, 'Подготовка презентации', 31, '2023-04-22 21:16:13.930967');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (34, 'Проверка домашнего задания', 31, '2023-04-22 21:16:24.628815');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (35, 'Запись видео', 31, '2023-04-22 21:16:31.844549');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (36, 'Подготовка презентации', 32, '2023-04-22 21:17:13.913118');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (37, 'Запись видео', 32, '2023-04-22 21:17:22.855665');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (38, 'Подготовка презентации', 33, '2023-04-22 21:18:09.117166');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (39, 'Проверка домашнего задания', 33, '2023-04-22 21:18:15.364398');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (40, 'Подготовка теста', 33, '2023-04-22 21:18:20.396001');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (41, 'Подготовка презентации', 34, '2023-04-22 21:18:51.847836');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (42, 'Запись видео', 34, '2023-04-22 21:18:58.358079');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (43, 'Подготовка теста', 34, '2023-04-22 21:19:03.903398');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (44, 'Подготовка презентации', 35, '2023-04-22 21:19:29.759451');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (45, 'Проверка домашнего задания', 35, '2023-04-22 21:19:36.844497');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (46, 'Видео', 35, '2023-04-22 21:19:42.013436');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (50, 'Подготовка презентации', 39, '2023-04-24 19:11:50.088096');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (51, 'Запись видео', 39, '2023-04-24 19:11:56.320237');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (52, 'Проверка домашнего задания', 39, '2023-04-24 19:12:05.391783');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (53, 'Подготовка презентации', 40, '2023-04-24 19:12:37.243884');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (54, 'Подготовка теста', 40, '2023-04-24 19:12:44.403425');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (55, 'Запись видео', 41, '2023-04-24 19:13:25.51433');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (56, 'Подготовка теста', 41, '2023-04-24 19:13:36.733695');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (57, 'Проверка домашнего задания', 41, '2023-04-24 19:13:47.935434');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (58, 'Проверка теста', 41, '2023-04-24 19:13:59.809488');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (59, 'Подготовка презентации', 42, '2023-04-24 19:14:43.882868');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (60, 'Запись видео', 42, '2023-04-24 19:14:51.591691');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (61, 'Подготовка олимпиады', 44, '2023-04-24 19:24:34.697935');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (65, 'Проверка домашнего задания', 45, '2023-04-24 19:31:14.839128');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (64, 'Организация воркшопа', 45, '2023-04-24 19:31:09.027762');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (63, 'Подготовка презентации', 45, '2023-04-24 19:31:01.25358');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (68, 'Проведение семинара', 46, '2023-04-24 19:31:56.922713');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (69, 'Создание онлайн-теста', 46, '2023-04-24 19:32:05.817126');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (66, 'Разработка набора задач', 46, '2023-04-24 19:31:42.601529');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (62, 'Создание интерактивных визуализаций', 45, '2023-04-24 19:30:55.771403');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (67, 'Подготовка видеоурока', 46, '2023-04-24 19:31:51.246538');


--
-- Data for Name: activity_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (9, 131898478, 19, 2.00, '2', '2023-04-22 21:58:18.287134');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (10, 131898478, 20, 1.00, '1', '2023-04-22 21:58:33.632238');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (11, 131898478, 23, 2.00, NULL, '2023-04-22 21:58:51.287484');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (13, 131898478, 35, 2.00, NULL, '2023-04-22 22:28:02.361982');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (14, 131898478, 35, -2.00, '-2', '2023-04-22 22:28:31.295092');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (15, 131898478, 37, 1.12, NULL, '2023-04-23 23:02:36.921593');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (16, 131898478, 51, 1.50, '1,,5', '2023-04-24 19:21:20.170213');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (17, 131898478, 69, 1.00, 'Сложный тест!', '2023-04-24 19:34:21.818621');


--
-- Data for Name: course_join_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('TXq54kwlZjH6', 24, 'Примечание тест', NULL, '2023-04-22 14:41:05.702463');
INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('a82TLzWc7FMP', 24, 'Мой код!', 131898478, '2023-04-22 15:03:34.051835');
INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('SBJ5iWf3rPyQ', 26, NULL, 131898478, '2023-04-24 19:20:40.232737');
INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('RM2a9Xtk1yTn', 27, NULL, 131898478, '2023-04-24 19:32:36.176607');


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.courses (course_id, name, description, created_at) VALUES (24, 'Математика 5-6', 'Математика для 5-6 классов', '2023-04-22 14:22:53.665567');
INSERT INTO public.courses (course_id, name, description, created_at) VALUES (26, 'Математика 7-8', NULL, '2023-04-24 19:11:28.436955');
INSERT INTO public.courses (course_id, name, description, created_at) VALUES (27, 'Программирование 10-11', 'Курс по подготовке к олимпиадам школьников старших классов', '2023-04-24 19:30:32.640656');


--
-- Data for Name: excel_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.excel_reports (report_id, file_data, created_at) VALUES (31, '\x504b0304140000000800519c9856465ac10c82000000b100000010000000646f6350726f70732f6170702e786d6c4d8e4d0bc2301044ff4ae9dd6e55f0203120d4a3e0c97b4837369064437685fc7c53c18fdb3cde308cba15ca58c423773586c4a77e11c94700b60b46c343d3a91947251a69581e40ce798b13d967c424b01bc70360154c33ce9bfc1decb53ae71cbc35e229e9abb785989c74976a3128f8976bf38e85d7bc1fb66ff96105bf93fa05504b0304140000000800519c98564064042ced000000cb01000011000000646f6350726f70732f636f72652e786d6c9591c14ec3300c865f65eabd75db1424a2ac17102790909804e21625de16ad49a3c4a8dddb9396ad1b820bc7f8fffcd95684f25cf5015f42ef3190c1b81a6de722577e9ded893c07886a8f56c622112e85db3e5849e91976e0a53ac81d425d96b76091a496246112e67e316627a5568bd27f866e166805d8a1454711aaa2820b4b186cfcb3614e16728c66a186612806367369a30ade9f9f5ee7e573e32249a7306b85565c0594d48776bac81fc74ec055519c667f1750afd2044e478febec9cbcb1fb87cd63d6d665cdf2b2c9eb6653dd71d670567f4cae1ffd17a1edb5d99a7f1a6fae8c67412be0d7bfb55f504b0304140000000800519c9856995c9c23100600009c27000013000000786c2f7468656d652f7468656d65312e786d6ced5a5b73da38147eefafd07867f66d0bc63681b6b413736976dbb49984ed4e1f8511588d6c796491847fbf473610cb960ded924dba9b3c042ce9fbce4547e7e83879f3ee2e62e8868894f27860d92fdbd6bbb72fdee057322411413019a7aff0c00aa54c5eb55a6900c3387dc91312c3dc828b084b7814cbd65ce05b1a2f23d6eab4dbdd5684696ca1184764607d5e2c6840d054515a6f5f20b4e51f33f815cb548d65a30113574126b988b4f2f96cc5fcdade3e65cfe93a1d32816e301b58207fce6fa7e44e5a88e154c2c4c06a673f566bc7d1d2488082c97d9405ba49f6a3d31508320d3b3a9d58ce767cf6c4ed9f8ccada74346d1ae0e3f17838b6cbd28b701c04e051bb9ec29df46cbfa44109b4a369d064d8f6daae91a6aa8d534fd3f77ddfeb9b689c0a8d5b4fd36b77ddd38e89c6add0780dbef14f87c3ae89c6abd074eb692627fdae6ba4e916684246e3eb7a1215b5e540d32000587076d6ccd203965e29fa75941ad91dbbdd415cf058ee398911fec6c504d669d219963446729d90050e0037c4d14c507caf41b68ae0c292d25c90d6cf29b5501a089ac881f5478221c5dcaffdf597bbc9a4337a9d7d3ace6b947f69ab01a7edbb9bcf93fc73e8e49fa793d74d42ce70bc2c09f1fb235b6187276e3b13723a1c67427ccff6f691a52532cfeff90aeb4e3c671f5696b05dcfcfe49e8c7223bbddf6587df64f476e23d7a9c0b322d7944624459fc82dbae41138b5490d32133f089d86986a501c02a4093196a186f8b4c6ac11e0137db7be08c8df8d88f7ab6f9a3d57a15849da84f810461ae29c73e673d16cfb07a546d1f655bcdca3975815019718df34aa352cc5d67895c0f1ad9c3c1d1312cd940b06418697242612a9397e4d4813fe2ba5dafe9cd340f0942f24fa4a918f69b323a77426cde8331ac146af1b758768d23c7afe05f99c350a1c911b1d02671bb346218469bbf01eaf248e9aadc2112b423e6219361a72b51681b671a984605a12c6d1784ed2b411fc59ac35933e60c8eccd9175ced6910e11925e37423e62ce8b9011bf1e86384a9aeda2715804fd9e5ec349c1e882cb66fdb87e86d5336c2c8ef747d4174ae40f26a73fe9323407a39a5909bd84566a9faa87343ea81e320a05f1b91e3ee57a780a3796c6bc50ae827b01ffd1da37c2abf882c0397f2e7dcfa5efb9f43da1d2b737237d67c1d38b5bde466e5bc4fbae31dad7342e28635772cdc8c754af9329d8399fc0ecfd683e9ef1edfad92484af9a592d2316904b81b34124b8fc8bcaf02ac409e8645b2509cb54d365378a129e421b6ee953f54a95d7e5afb928b83c5be4e9afa1743e2ccff93c5fe7b4cd0b3343b7724beab694beb526384af4b1cc704e1ecb0c3b673c921db677a01d35fbf65d76e423a530539743b81a42be036dba9ddc3a389e9891b90ad352906fc3f9e9c5781ae239d904b97d98576de7d8d1d1fbe7c151b0a3ef3c961dc788f2a221eea18698cfc34387797b5f986795c65034146d6cac242c46b760b8d7f12c14e064602da00783af5102f2525560315bc6032b90a27c4c8c45e870e7975c5fe3d192e3dba665b56eaf2977196d225239c269981367abcade65b1c1551dcf555bf2b0be6a3db4154ecffe59adc89f0c114e160b1248639417a64aa2f31953bee72b49c45538bf4533b6129718bce3e6c7714e53b81276b60f0232b9bb39a97a653167a6f2df2d0c092c5b885912e24d5dedd5e79b9cae7a2276fa9777c160f2fd70c9470fe53be75ff45d43ae7ef6dde3fa6e933b484c9c79c5110174450223951c06161732e450ee9290061301cd94c944f0028264a61c8098fa0bbdf20cb92915cead3e397f452c83864e5ed22512148ab00c05211772e3efef936a778cd7fa2c816d84543264d517ca4389c13d337243d85425f3aeda260b85dbe254cdbb1abe26604bc37a6e9d2d27ffdb5ed43db4173d46f3a399e01eb387739b7ab8c245acff58d61ef932df3970db3ade035ee6132c43a47ec17d8a8a8011ab62bebaaf4ff9259c3bb47bf181209bfcd6dba4f6dde00c7cd4ab5aa5642b113f4b077c1f9206638c5bf4345f8f1462ada6b1adc6da310c798058f30ca16638df87459a1a33d58bac398d0a6f41d540e53fdbd40d68f60d341c91055e3199b636a3e44e0a3cdcfeef0db0c2c48ee1ed8bbf01504b0304140000000800519c9856e865871d9c060000502e000018000000786c2f776f726b7368656574732f7368656574312e786d6cdd5a5b73a336147eefaf60dc99be35a02340401c4f6d763aed43677676a7ed331b93c4b3b671816cda7f5f21898be0c862dd26bbd917637174c4b94b9fa4e553517eac1ef2bc76fe3eec8fd5cde2a1ae4f89eb56b70ff921abae8a537ee494bba23c64356f96f76e752af36c2b980e7b173c2f740fd9eeb8582dc5bbb7e56a593cd6fbdd317f5b3ad5e3e19095ff6cf27df174b3208bf6c5bbddfd432d5eb8abe529bbcfdfe7f5ef27cec09b6e37ce7677c88fd5ae383a657e77b35893e40d952ca2cb1fbbfca91afc771a6d3e14c5c7a6f1ebf666e13542e5fbfcb66ec6c8f8e3539ee6fb7d331417e52f35eaa2ff6ac339fcdf0effb3300097ef4356e569b1ff73b7ad1f6e16d1c2d9e677d9e3be7e573cfd922ba50231e06db1afc4aff3243b037f7ffb58d5c54171f30f1f76474ee0cfec6ff174e77150c541c71c243270f88ac397ca4ae1846a6fb23a5b2dcbe2c9299bee7cb8e68f309060e71aed8e8d3bdfd725a7ee385fbdfae17be2f9fe75f360201eb1d7b692a55bf34f341ddd5b35dc460e0762b826563eadfcc0f3bdab88046110c5be17d1a5fb4972b85c984e22e8240231043d235120258a987c4889a2782866140c698c5d3ba2a9742092188d18518da438fe3971003390120e335e2b71c7278463a17c4b9b07f1e8b513fc180ec596944ec3587b4866e65feb3a6836a69d8da9502a302a15f9ccbbc6ac6163e4d68835e386adaac868a97d345f33956e3fe66bae0e87f6903d89876af166fe77e5d8ad6b22cdb5e4fabb9faaec70e285c7dbe667ecee7776f7c587c3417a902e1da481650f3623fa63447b659238d6e2bd358d8a45aa05618005a8a6af1eae116ad254ca1d9d935b97543db497fae75bffea69d266bde60b166b9e0946a54ab47c4d193c30a416f1c03f8097aba07369200ba8a77844a1169e3411d2c06a2a9f69998ed4b926b29da1913ccdaaacb523a664305192e04a869d92a1d4854c943411d2f0a5e261546fe391eb3103849a01c44439549b756ab349bac2285d650f02e79c0943e9db800d91801dcd569c03d310c94de2b5c608a6a1d231523471d93791b8ecbc4ba3cea591295d4d84349a6da0083102d3b4364cf97a7d566a875a7d6623ab3b43eb81e6196405d42c2730b34573eb5ddc193036950213218dbf70bd8bcfc706f1fac5b03749783a4a78d5e5dc04ed532c5fb57068f3459b6063cdd5edfc0e9abeec4c2eb58147351a0cf36c149bf32325557abff63aa1d43007c300191153a41b29a9a27cb958570298f5eb71168149b0fbe36007fbf4166862c533e6351d7e316d7ad4cb9dcecf17dc8e6a3a485f6cb8d138fae2608c95940be1db0874b004420f060935cd89464aaa28dfe6aca89433dbae0774c43716091325252f86952e581b13dfa27b8f7c48302920c1b8800476388bede2a09b281daa45016c07ca8779a346a3ffb9f0a095c20ee45e45a5082c1eef6120098d95c24449891d093ef39468817ba4c77b8419b3d94449c98b01a84bb2d9828b480f8c4834c9e6709ccdd18ce5c067ec4ea1b98e2d69672c9e0ddb52643e7afbaa7334b2f8b1c7672436e6a88992123b447bc5b3b905ff418fffc033e5bf9192821d183d6f7d030ba4811ed20099e4381be5b8ea7216df02e6f5b0f5c13061ce6fcdebab79f498c97e8a720e354b0671968296cce9687a97c9410d5662c08ef95e4389010b7284c1091d18d3c44449c10eab9e394d744024b6bdaf8861bb0b7a7404749233d13867e8ff3a2fa2f39b1e2da3c4ba787a84f930eeab8e5d0b60831eb0816f9a1e8d9414e603b6d7373d8205f0410ff82030e6bd8992c28b81a40b96c760813ed0431f082765201e9781d00e762fbc2af039931cd54ca503d9514eb653af969473b6f0ce451d9755db9e83d972c538ce86173b4b7cde2265c1a1d0e35060c62265a2a460c7a1cf3cc15ab026f45813226321315152783124774921b1e033e8f119c4d33b20deb892c4cfb1ef7e41d232dd4e6abcc8feadaeb4e8a758fad9f5fc1b3b29cc47a85f750db06051da6351ea996a809192d2f98774af6fa1422d3897f638971a8fee8c9494ce38bad3cf62e714456a4255eee052e6212fefc585d5cab92d1e8fb5c2ecddebf65a2c24e2bcc19d92204c4451c54871b256b76947a40d0912b1b18971d1442cf7102e48524079fca4b9278470f8c9062770b13706b1b96c6b5cb60d4b9abb06983e5e22ce66317d4822602bc605c9c660563ee01a1f7043a2446c0a615ad16483db6ecd92352e3af7d2c6e0252efa06177dcd85582b21dc3e88e44debdfb2f27e77ac9c7d7ec703cabb625ca252de5c968dba38898bbf1f8aba2e0ee2ef439e6df3b2e9c0e9774551778de60bdd25f2d5bf504b0304140000000800519c9856452da990390400000a15000018000000786c2f776f726b7368656574732f7368656574322e786d6cdd585b8fa336147eefaf40a9d4c7c106830db9a8134655fb5069b5ab6d9f99c449d0024ec1996cff7d8d6d08267632adbad79710fbf81c9fef3b178c1767d67c680f9472ef6355d6ed7276e0fc98fa7ebb39d02a6f1fd891d642b2634d9573316cf67e7b6c68be954a55e90700c47e9517f56cb590736f9ad5829d7859d4f44de3b5a7aaca9bbfd7b464e7e50ccefa89b7c5fec0e584bf5a1cf33d7d47f9fba35010437fb0b32d2a5ab705abbd86ee96b347983ec148aac8257f14f4dc8efe7b1d9a67c63e7483dfb6cb19e89ca225ddf0ce462e1e2f34a365d99912aefca5adce2ebb769ae3ffbdf95f2401c2bfe7bca5192bff2cb6fcb09c9199b7a5bbfc54f2b7ecfc2bd5a0948b1b56b6f2d73babc58198df9c5ace2aad2d36ae8a5a08c433ff289ffeeb3442ad114e3520716820ad811458e59c84f694f37cb568d8d96bbae5c25cf7471224d505a2a2eec2f98e37425a083dbefae94708109a770f1cc84702fa51baf0b9d8a25be86fb4b9b5321748735daebcac5004107820308ae30490208c16fe8bd2f085338347c1e051204d84373c8a944704ab87f288246337493496613cf7e45063804a48268a5644ca1da4114956c77e8783dfa15c1839fd260883b96d877b8a027062381ccf35188bb5ecbe3504e6633280c11432e88bc70ca9951058513cbd7e5f651bc7634c58c712ce7ff8b9cdaba32866b0a5e63e06ef68e01dc98de351cac121c514c16a05be453030f0ea8c0f8dfc8a2c65400c10c42016dbe3a39c21b79c31c8d73c6163d2dcbe0fdab0af372e0f83609c187447939a96236480b1475ba1485c55110dd189547f01a3952a282e4116dd250861a3d42d6da04b526f4c0d30b8c43d7b366891014de6d383a369c503cc58a18157305d822c7e751e104bacb111dc49e4fbd232b359473736b2194f92cb1b274960906669ac1084560ae3dbd98107daf055ed0693da552b60708b273289ea5549767e4a6489f15a20663158b164f8bba8577c3b226488087125b24b9091cf4550020c2e92091736d8e436ec64809d5c25623849c4e4ee4b0485b63c34eab587394d4e5be2255fb80f26b7b983e0728604ae26ef94645af275a68d76ce8d7d747e864eec2e49a625df67efd7e0dcdc5d4efa3070351ba724d3924fc2dd7fc994e00edacbf7010caf7a0c9af418bde4e6dbae3f4587e3e8f5b10c8d5788fd00aa37f9d6df681a869bf9cb170244ce3c73493278ff9cfe69db2fbc73c4869733368cae322b9e6656f4afcf51c88ce59068aa54e024e0d7bde3f2c164cdc2fbc7fcff2b0be371c1f4f1b15d21984d2f49ec71891c71f147d72c156df6f20aaaf536ec5473fdca18a6d545d73a4833751934113ca2b4fba2b008925476cd6bc91aa56babca3a49d77615d19152591b1625215adb458ffadeeb4ac33afd88d3ee4869598fd3b512f817b2d41de1ef79b32fead62be94e10071eb0b0dca83b3735e0ec28afac9e19e7ac927f0f34dfd2a65b20e43bc6f830e87618ae3f57ff00504b0304140000000800519c985603cab713490400007412000018000000786c2f776f726b7368656574732f7368656574332e786d6cbd585b8fe236147eefaf8852a96f9d38573b0ca00e1955edc34aab5dedf6390306a2cd852666d8fefb3abe049fe00454b57dc1b18fcfed3b171b2f2f4dfbad3b52ca9cef5559772bf7c8d869e179ddf648abbc7b6a4eb4e6947dd35639e3d3f6e075a796e63bc154955e8050e2557951bbeba558fbd8ae97cd9995454d3fb64e77aeaabcfd6b43cbe6b2727d572f7c2a0e472616bcf5f2941fe867cabe9c38039f7a839c5d51d1ba2b9ada69e97ee5bef88b575fb2882d5f0b7ae98c6fa7f7e6ad69bef593df772b17f546d1926e592f23e7c33bcd6859f6a2b8297f2aa9ee556bcf697e6bf1bf0a00b87d6f7947b3a6fca3d8b1e3ca25aeb3a3fbfc5cb24fcde537aa9c8a85c06d5376e2d7b9c8cd015fdf9e3bd6548a9b2bae8a9a13f8987f17a3f71847a838c231874f263822c5114967a571c2b5d79ce5eb65db5c9cb6dfcec5f51f0220c1ce3d2aea3e9c9f59cba905e763eb9f7ef451143df7030ec490223d5b2c3dc655f41bbdad12b791e20221aecf95f77514a3083d113f4e30c1849068e9bd4b0e8f1b3358140c160542443863512c2d22580ed222929a6692d8a461fcec88a9f2c197443262b47a24cd89e6cc4176a98e6964329e0a9d6a88cd4585b0dea27c0dc68e38c6261202246cf0285cb4c640ef1462d2c4540284fa085900853bb112a3904c8146858756a1b00a414094fd9a2305c3a0034607644f38644f28c2154f868b44183ddbe27c8f91c73905011e30b348cbee4b8b00923ae808041de40540b70f8b45efebe37a63331f944f58a58cfffcc32f5d5e9d784b453b3a837b34e01e09c58951f8fe50e81260b9033f605a68a90a8d3a0270499cd29b5abbed0bba8074e12090b250090c068c37ac47628d42265d2573b9144fcbd6512036c375c0121300dd9b13105a3c8251f28336396a07668dfb28b46698f42d558116a78c9911f19011b13c5990b15326c214218befc31681748d675a3ef0338d469e39662c130bde29c4196b693648e27948920192640a922942963c9c49fff4440960ed8046a041c426c0b0bd036427eae1359907080f006189837f03d01421c3f70182476e7a2ff1af872cb2b90d710a1e6de2690a0e3e0c605346a91b040687e2fd7ceefbb50d753c8f3a19502737bd3b18f56eb9c30fee5f132168d77b86d9bc417f82fd594709dbb292c0e4263615d00a6b7b9d88b9ad91937fa391e304f86bcf35586973580e6edb624ee6639e0e314fa75ad114214bffc34a0307d7e836e86bdacf96321cdf386d98a40013783501e8f8e8fab7084de13349c91465162100064e47111543686bdda3661d4f735ca5dd3def7921daf0527e4c26916ffc7bf4a71af624255394ffe14c1b3559588689d9726feef433e9a4ecbf85c733fe6757b43d883788ced936e79ac98bd1b0aa1e3aa2457fe27937844db0c8021be1852c5ed4d3c898852c36139468b1915abcab55f235e643de1e8aba734abae716a227cc6f32ad7cdd9013d69cc4e3c05bc3585389cf23cd77b4ed3770fabe69d830e9350c0f4debbf01504b0304140000000800519c985698c432f85d030000d81300000d000000786c2f7374796c65732e786d6cdd586d6f9b3010fe2b88ef2d496851a842a42d5dd549cb54a9fdb07d748209966ccc8cd325fdf5f3d98490974bdf92751aa8c5be87e7eef1f9b0dd0e2abde4f43ea7547b0bc18b2af173adcbab20a8a63915a43a97252d0c92492588365d350baa5251925640123ce8753a5120082bfce1a0988b1ba12b6f2ae7854efc5e63f2dce36b9af8dde8c2f79cbb914c69e22fcd7526c4599a7af995105755e57bc15ee2e526f1fafa7c3c3eff692eeff6f66a3cb6b4a0d6301c64b2d8940206e39708ea3d129ef823c2d944314bcb88607ce9ec3d6b994a2e95a74d164ca8ae35554fee856edd8514d5be042ba472025c18f77b5213da887d803ec679a3efc27786e1a0245a5355dc988e2359eb2e56b71f96a5d1375364d9ed5dfa2f675492b31482ce4676a06a3649fc4ee78bbdad9f098a042dafef8c7763af7df15ac8de78f661d238912aa5aa49e4a5bf320d079c661af88acd72dbd0b2b491a4d652402b6564260be232bda26dd0ed0792f83a3705bef6b56d05c7dbb63acab6f935614e2df92f38de46f746a91b6636a794f37ba0fcc89a29ed9a295d64ad95a003eb40d1344d1dd44de7a6ee4080b63be7bced377c9be3923d4afd796e8657d8feafb9d4f44ed18c2d6c7f91ad1560eebb27705f2f90cfea2765c9979f389b1582bafcbe38e67040563c2f978a3d9968b0c04179b88c2fb2370dfa489a7e2b523ed0856e96dc43723e22458f54693685fed4bc40d5db93d63d89ca95aa5725f26324be2b95bdd3e8dcd574948a3c9ec07f4cce71e615d3191e67adc6dc5f1c7d2b083fb42a837a7f6cedc21b7b7063f5e00c9df8dfe12cce5b839ccc19d7aca87b394b535aec6ec5c6bf2613f357c74600f3564a3332e7faa101137fdd1ed394cd45dcbc750779a8df5ab7bfc189a41bad0ff026182b52baa0e9a8ee9ae3e5c639d35dee3cb305b58ea0bb10ca7220020188c64265a02cc74363fd8fe3eae3e37220aab0bf1feae3ac3ece72bcbdd0c8de682c84159b0b19721c876114a1e91d8df6cb18a1398c22f8411ca20a8183c68268afcdfc8102385036cfd4063acb07cb061df2811245877c20f3002139044e1c230580c6020e3a29684581082416941ac20a4398675421fa991f80e21885a04891ea8d222c5111dcc87ca11f5118c631020188c8084314820ff60084ca00212814866e23dddacf82d53e17acff9737fc03504b0304140000000800519c9856b747eb8ac0000000160200000b0000005f72656c732f2e72656c739d924b6e02310c40af12655f4ca9c40231acd8b043880bb889e7a399c49163c4f4f68dd8c02068114bff9e9e2daf0f34a0761c73dba56cc630c45cd95635ad00b26b29609e71a2582a354b402da13490d0f5d8102ce6f325c82dc36ed6b74c73fc49f40a91ebba73b465770a14f501f8aec39a234a435ad97180334bffcddccf0ad49a9dafacecfca735f0a6ccf3f52090a24745702cf491a44c8b7694af3e9eddbea4f3a56362b478dfe8fff3d0a8143df9bf9d30a589d2d74509266fb0f905504b0304140000000800519c9856fb7f7d3e86010000eb0200000f000000786c2f776f726b626f6f6b2e786d6c8d92cd4a243110c75fa5c97decee719dd5c1f6a2e80acb2a2ade33ddd576613e9a24e3ec7a129f43f015066540447d86f84656d28c3608ba9754fe55c5af3e92cd9936e713adcf93bf52283b36056b9c6bc7696acb0624b72bba0545b15a1bc91d497396eabac61276743995a05c3accb2516a4070875ad9065bcb3adaffb06c6b8057b60170527428c951b1adcd6567872649fb4a3b2843a5e00d9e538499fd480832b9408b1314e8fe152cde05b044a242899750152c63896df4ec973678a995e3e2b8345a8882e55de0148cc3f293fb38b479c227367a1c9f1c85990b36ca0858a3b12e66443ea7262f80923b35757a178503b3c31dec193d6d519d450c8d91f6e688ab58da44710905f3377efe7aed17fe29da07ffe8e7c9da6014baa2acfdaaebd011ba37af192305cc7ed515f916f873b0de030ebf000e3f036f5faffc8bbfa7734ed027ff10f51da967c22f923c1be4790fbffa057eb55bca721315d4a8a0fa43856c08d0bb94f4298289930f7face51bb4ffa910dbe43b50bf35afde57bbfc175b6f504b0304140000000800519c98560b085d06bc0000001f0300001a000000786c2f5f72656c732f776f726b626f6f6b2e786d6c2e72656c73cd93390e83301045af62f9000c4b922282546968232e60c1b088c59667a2c0ed83a0004b29d2a0a4b2fe587eff15e3f8819de2460f543786c4d8770325b266365700ca6bec1579dae030df94daf68ae7682b302a6f558510fafe05ec9e216ff19e29b2c9e037445d964d8e779d3f7b1cf803185edab65423b21499b215722261ecb631c17204de4c96222d1269d32290027e6d143a46e11f18458e5174a411f1d4216d3a6b76fa4f47f6f3fc16b7fa25ae437751ce8b0438ffe1f606504b0304140000000800519c9856dbfbce8f24010000e9040000130000005b436f6e74656e745f54797065735d2e786d6ccd54cb4ec33010fc95c8d72a71291207d4f4025ca1077ec0249bc68a5ff26e4bfaf76c121a09545aaa20d14bac786767c63bb297affb0098b4d638cc454d14eea5c4a206ab30f3011c572a1fad22fe8d1b1954d1a80dc8c57c7e270bef081ca5d47188d5f2112ab535943cb5bc8ddabb5c443028928701d869e542856074a188eb72e7ca6f2ae9a742c69d3d066b1d70c60091c8a3127de9478543e3cb0e62d425246b15e9595986c9d648a4bd01cc4e731c71e9ab4a1750fa626bb925c310419558039035d9403a3b234d3c6418be37930df434271519ba8e3e20a716e172bd432c5d771a980822e933871c25997bf209a14bbc84f2b7e23ce1771f9b3e1394fd327dcc5f731ef92f35b2b81623b7ff69e4cdfbe6af6f5eb7665669371a90fd0bb7fa00504b01021403140000000800519c9856465ac10c82000000b1000000100000000000000000000000800100000000646f6350726f70732f6170702e786d6c504b01021403140000000800519c98564064042ced000000cb0100001100000000000000000000008001b0000000646f6350726f70732f636f72652e786d6c504b01021403140000000800519c9856995c9c23100600009c2700001300000000000000000000008001cc010000786c2f7468656d652f7468656d65312e786d6c504b01021403140000000800519c9856e865871d9c060000502e000018000000000000000000000080810d080000786c2f776f726b7368656574732f7368656574312e786d6c504b01021403140000000800519c9856452da990390400000a1500001800000000000000000000008081df0e0000786c2f776f726b7368656574732f7368656574322e786d6c504b01021403140000000800519c985603cab713490400007412000018000000000000000000000080814e130000786c2f776f726b7368656574732f7368656574332e786d6c504b01021403140000000800519c985698c432f85d030000d81300000d00000000000000000000008001cd170000786c2f7374796c65732e786d6c504b01021403140000000800519c9856b747eb8ac0000000160200000b00000000000000000000008001551b00005f72656c732f2e72656c73504b01021403140000000800519c9856fb7f7d3e86010000eb0200000f000000000000000000000080013e1c0000786c2f776f726b626f6f6b2e786d6c504b01021403140000000800519c98560b085d06bc0000001f0300001a00000000000000000000008001f11d0000786c2f5f72656c732f776f726b626f6f6b2e786d6c2e72656c73504b01021403140000000800519c9856dbfbce8f24010000e90400001300000000000000000000008001e51e00005b436f6e74656e745f54797065735d2e786d6c504b0506000000000b000b00ca0200003a2000000000', '2023-04-24 19:34:35.468468+00');


--
-- Data for Name: lessons; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (26, '2023-01-10 00:00:00+00', 'Основы комбинаторики', 24, '2023-04-22 21:12:19.332979', '2023-01-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (27, '2023-01-17 00:00:00+00', 'Введение в теорию чисел', 24, '2023-04-22 21:13:06.612021', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (28, '2023-01-24 00:00:00+00', 'Геометрические преобразования', 24, '2023-04-22 21:14:00.572644', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (29, '2023-01-31 00:00:00+00', 'Решение уравнений и неравенств', 24, '2023-04-22 21:14:31.089253', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (30, '2023-02-07 00:00:00+00', 'Системы линейных уравнений', 24, '2023-04-22 21:15:26.508318', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (31, '2023-02-14 00:00:00+00', 'Основы стереометрии', 24, '2023-04-22 21:16:08.076629', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (32, '2023-02-21 00:00:00+00', 'Вероятность и математическая статистика', 24, '2023-04-22 21:17:06.771508', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (33, '2023-02-28 00:00:00+00', 'Основы тригонометрии', 24, '2023-04-22 21:18:00.579455', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (34, '2023-03-07 00:00:00+00', 'Математическая логика и решение задач на логику', 24, '2023-04-22 21:18:45.705509', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (35, '2023-03-14 00:00:00+00', 'Решение задач на движение и скорость', 24, '2023-04-22 21:19:24.3484', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (39, '2023-02-01 00:00:00+00', 'Комбинаторика', 26, '2023-04-24 19:11:44.374362', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (40, '2023-02-08 00:00:00+00', 'Теория чисел', 26, '2023-04-24 19:12:31.989172', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (41, '2023-02-15 00:00:00+00', 'Геометрия', 26, '2023-04-24 19:13:17.191594', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (42, '2023-02-22 00:00:00+00', 'Алгебра', 26, '2023-04-24 19:14:33.735918', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (43, '2023-03-08 00:00:00+00', NULL, 26, '2023-04-24 19:15:11.124794', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (44, '2023-03-15 00:00:00+00', NULL, 26, '2023-04-24 19:24:19.980433', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (45, '2023-04-01 00:00:00+00', 'Алгоритмы поиска и сортировки', 27, '2023-04-24 19:30:49.742709', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (46, '2023-04-08 00:00:00+00', 'Динамическое программирование', 27, '2023-04-24 19:31:36.802559', '2023-05-17 00:00:00+00');


--
-- Data for Name: teacher_courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.teacher_courses (teacher_id, course_id, created_at) VALUES (131898478, 24, '2023-04-22 15:03:36.704994');
INSERT INTO public.teacher_courses (teacher_id, course_id, created_at) VALUES (131898478, 26, '2023-04-24 19:20:43.821959');
INSERT INTO public.teacher_courses (teacher_id, course_id, created_at) VALUES (131898478, 27, '2023-04-24 19:32:39.823423');


--
-- Data for Name: teachers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.teachers (comment, created_at, teacher_id, is_manager) VALUES (NULL, '2023-04-16 10:45:35.442808', 438003435, false);
INSERT INTO public.teachers (comment, created_at, teacher_id, is_manager) VALUES (NULL, '2023-04-09 21:48:37.86559', 131898478, true);


--
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activities_id_seq', 69, true);


--
-- Name: activity_records_record_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activity_records_record_id_seq', 17, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_id_seq', 27, true);


--
-- Name: excel_reports_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.excel_reports_report_id_seq', 31, true);


--
-- Name: lessons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lessons_id_seq', 46, true);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (activity_id);


--
-- Name: activity_records activity_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records
    ADD CONSTRAINT activity_records_pkey PRIMARY KEY (record_id);


--
-- Name: course_join_codes course_join_codes_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_join_codes
    ADD CONSTRAINT course_join_codes_code_key UNIQUE (code_id);


--
-- Name: course_join_codes course_join_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_join_codes
    ADD CONSTRAINT course_join_codes_pkey PRIMARY KEY (code_id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (course_id);


--
-- Name: excel_reports excel_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.excel_reports
    ADD CONSTRAINT excel_reports_pkey PRIMARY KEY (report_id);


--
-- Name: lessons lessons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_pkey PRIMARY KEY (lesson_id);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (teacher_id);


--
-- Name: teacher_courses unique_teacher_course; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT unique_teacher_course UNIQUE (teacher_id, course_id);


--
-- Name: activities activities_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.lessons(lesson_id);


--
-- Name: activity_records activity_records_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records
    ADD CONSTRAINT activity_records_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(activity_id);


--
-- Name: course_join_codes course_join_codes_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_join_codes
    ADD CONSTRAINT course_join_codes_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id);


--
-- Name: teacher_courses fk_teachers; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT fk_teachers FOREIGN KEY (teacher_id) REFERENCES public.teachers(teacher_id);


--
-- Name: activity_records fk_teachers; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records
    ADD CONSTRAINT fk_teachers FOREIGN KEY (teacher_id) REFERENCES public.teachers(teacher_id);


--
-- Name: lessons lessons_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id);


--
-- Name: teacher_courses teacher_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT teacher_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

