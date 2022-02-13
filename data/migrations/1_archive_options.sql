ALTER TYPE option ADD ATTRIBUTE archived timestamptz;

ALTER TABLE options ADD COLUMN archived timestamptz DEFAULT NULL;

DROP VIEW options_extended_view CASCADE;

CREATE VIEW options_extended_view AS
SELECT
    NULL::integer AS id,
    NULL::integer AS poll_id,
    NULL::text AS label,
    NULL::bigint AS author,
    NULL::bigint[] AS votes,
    NULL::integer AS index,
    NULL::timestamptz AS archived;

CREATE VIEW grouped_options AS
 SELECT polls.id,
    array_agg(
        ROW(
            options_extended_view.id,
            options_extended_view.label,
            options_extended_view.author,
            options_extended_view.votes,
            options_extended_view.index,
            options_extended_view.archived
        )::option ORDER BY options_extended_view.index) FILTER (WHERE (options_extended_view.poll_id IS NOT NULL)) AS options
   FROM (polls
     LEFT JOIN options_extended_view ON ((polls.id = options_extended_view.poll_id)))
  GROUP BY polls.id;

CREATE VIEW public.polls_extended_view AS
 SELECT polls.id,
    polls.question,
    polls.author,
    polls.expires,
    polls.allow_multiple_votes,
    polls.message,
    polls.channel,
    polls.closed,
    grouped_options.options,
    grouped_allowed_voters.allowed_voters,
    grouped_allowed_vote_viewers.allowed_vote_viewers,
    grouped_allowed_editors.allowed_editors
   FROM ((((public.polls
     LEFT JOIN public.grouped_options ON ((polls.id = grouped_options.id)))
     LEFT JOIN public.grouped_allowed_voters ON ((polls.id = grouped_allowed_voters.id)))
     LEFT JOIN public.grouped_allowed_vote_viewers ON ((polls.id = grouped_allowed_vote_viewers.id)))
     LEFT JOIN public.grouped_allowed_editors ON ((polls.id = grouped_allowed_editors.id)));

ALTER TABLE ONLY public.options
    DROP CONSTRAINT unique_options_poll_id_index;

ALTER TABLE ONLY public.options
    ADD CONSTRAINT unique_options_poll_id_index UNIQUE (poll_id, index, archived);
