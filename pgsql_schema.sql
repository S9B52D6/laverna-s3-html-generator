--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.8
-- Dumped by pg_dump version 9.6.8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_with_oids = false;

CREATE TABLE public.note (
    id uuid NOT NULL,
    title text,
    created timestamp without time zone,
    updated timestamp without time zone,
    notebook_id uuid,
    is_favorite boolean
);

CREATE TABLE public.notebook (
    id uuid NOT NULL,
    parent_id uuid,
    name text,
    count integer,
    created timestamp without time zone,
    updated timestamp without time zone
);

CREATE TABLE public.s3_keys (
    id integer NOT NULL,
    key text,
    size integer,
    storage_class text,
    last_modified timestamp without time zone
);

CREATE SEQUENCE public.s3_keys_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.s3_keys_id_seq OWNED BY public.s3_keys.id;
ALTER TABLE ONLY public.s3_keys ALTER COLUMN id SET DEFAULT nextval('public.s3_keys_id_seq'::regclass);

ALTER TABLE ONLY public.note
    ADD CONSTRAINT note_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.notebook
    ADD CONSTRAINT notebook_pkey PRIMARY KEY (id);

