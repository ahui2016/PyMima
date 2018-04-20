CREATE TABLE mima (
    nonce       varchar(32)    PRIMARY KEY,
    encrypted   bytea
);

CREATE TABLE history (
    nonce       varchar(32)    PRIMARY KEY,
    mimanonce   varchar(32)    NOT NULL
                               REFERENCES mima (nonce) ON DELETE CASCADE,
    encrypted   bytea
);
