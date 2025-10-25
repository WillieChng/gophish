
-- +goose Up
-- SQL in section 'Up' is executed when this migration is applied
ALTER TABLE groups ADD COLUMN risk_urgency varchar(10) DEFAULT 'medium';
ALTER TABLE groups ADD COLUMN risk_suspicious_links varchar(10) DEFAULT 'medium';
ALTER TABLE groups ADD COLUMN risk_generic_greeting varchar(10) DEFAULT 'medium';
ALTER TABLE groups ADD COLUMN risk_suspicious_sender varchar(10) DEFAULT 'medium';
ALTER TABLE groups ADD COLUMN risk_attachments varchar(10) DEFAULT 'medium';
ALTER TABLE groups ADD COLUMN risk_spelling_errors varchar(10) DEFAULT 'medium';

-- +goose Down
-- SQL section 'Down' is executed when this migration is rolled back

