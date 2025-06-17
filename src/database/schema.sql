-- HackerNews Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL,
    karma INTEGER DEFAULT 0,
    about TEXT,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_username ON users(username);

-- Stories table
CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    url VARCHAR(1024),
    text TEXT,
    score INTEGER DEFAULT 0,
    author_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_dead BOOLEAN DEFAULT FALSE,
    descendants INTEGER DEFAULT 0
);

CREATE INDEX idx_stories_created_at ON stories(created_at);
CREATE INDEX idx_stories_score ON stories(score);
CREATE INDEX idx_stories_author_id ON stories(author_id);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    author_id TEXT NOT NULL REFERENCES users(id),
    story_id INTEGER NOT NULL REFERENCES stories(id),
    parent_id INTEGER REFERENCES comments(id),
    created_at TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_dead BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_comments_story_id ON comments(story_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    url VARCHAR(1024),
    text TEXT,
    score INTEGER DEFAULT 0,
    author_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_dead BOOLEAN DEFAULT FALSE,
    job_type VARCHAR(50),
    location VARCHAR(255),
    company VARCHAR(255),
    salary_range VARCHAR(255)
);

CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_score ON jobs(score);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_author_id ON jobs(author_id);

-- Add foreign key constraints
ALTER TABLE stories
    ADD CONSTRAINT fk_stories_author
    FOREIGN KEY (author_id)
    REFERENCES users(id)
    ON DELETE CASCADE;

ALTER TABLE comments
    ADD CONSTRAINT fk_comments_author
    FOREIGN KEY (author_id)
    REFERENCES users(id)
    ON DELETE CASCADE,
    ADD CONSTRAINT fk_comments_story
    FOREIGN KEY (story_id)
    REFERENCES stories(id)
    ON DELETE CASCADE,
    ADD CONSTRAINT fk_comments_parent
    FOREIGN KEY (parent_id)
    REFERENCES comments(id)
    ON DELETE CASCADE;

ALTER TABLE jobs
    ADD CONSTRAINT fk_jobs_author
    FOREIGN KEY (author_id)
    REFERENCES users(id)
    ON DELETE CASCADE; 