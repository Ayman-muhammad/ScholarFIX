-- ScholarFix Database Schema
-- SQLite 3

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    user_type TEXT DEFAULT 'free',
    api_key TEXT UNIQUE,
    documents_count INTEGER DEFAULT 0,
    max_documents INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    profile_data TEXT DEFAULT '{}',
    
    CHECK (user_type IN ('free', 'student', 'professional', 'premium', 'admin'))
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_id TEXT UNIQUE NOT NULL,
    original_filename TEXT NOT NULL,
    processed_filename TEXT,
    mode TEXT DEFAULT 'academic',
    options TEXT DEFAULT '{}',
    status TEXT DEFAULT 'processing',
    metrics TEXT DEFAULT '{}',
    original_path TEXT,
    processed_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CHECK (status IN ('processing', 'completed', 'failed', 'queued')),
    CHECK (mode IN ('academic', 'cv', 'professional', 'personal'))
);

-- User statistics table
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY,
    total_documents INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0,
    grammar_fixes INTEGER DEFAULT 0,
    clarity_improvements INTEGER DEFAULT 0,
    tone_adjustments INTEGER DEFAULT 0,
    formatting_changes INTEGER DEFAULT 0,
    last_processed TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- API usage table (for rate limiting)
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time INTEGER,
    status_code INTEGER,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Document feedback table (for improvement)
CREATE TABLE IF NOT EXISTS document_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- System logs table (for monitoring)
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level TEXT NOT NULL,
    message TEXT NOT NULL,
    source TEXT,
    user_id INTEGER,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- User sessions table (for enhanced session management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Subscription plans table
CREATE TABLE IF NOT EXISTS subscription_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    max_documents INTEGER DEFAULT 5,
    price_monthly DECIMAL(10, 2),
    price_yearly DECIMAL(10, 2),
    features TEXT DEFAULT '{}',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User subscriptions table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    plan_id INTEGER NOT NULL,
    stripe_subscription_id TEXT,
    status TEXT DEFAULT 'active',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans (id),
    CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'trialing'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_file_id ON documents(file_id);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_mode ON documents(mode);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_timestamp ON api_usage(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX IF NOT EXISTS idx_document_feedback_document_id ON document_feedback(document_id);
CREATE INDEX IF NOT EXISTS idx_document_feedback_user_id ON document_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_document_feedback_rating ON document_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_period_end ON user_subscriptions(current_period_end);

-- Triggers for automatic updates

-- Update user document count when document is created
CREATE TRIGGER IF NOT EXISTS update_user_doc_count_insert
AFTER INSERT ON documents
BEGIN
    UPDATE users 
    SET documents_count = documents_count + 1 
    WHERE id = NEW.user_id;
    
    INSERT OR IGNORE INTO user_stats (user_id) VALUES (NEW.user_id);
    UPDATE user_stats 
    SET total_documents = total_documents + 1,
        last_processed = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id;
END;

-- Update user document count when document is deleted
CREATE TRIGGER IF NOT EXISTS update_user_doc_count_delete
AFTER DELETE ON documents
BEGIN
    UPDATE users 
    SET documents_count = documents_count - 1 
    WHERE id = OLD.user_id;
    
    UPDATE user_stats 
    SET total_documents = total_documents - 1
    WHERE user_id = OLD.user_id;
END;

-- Update user stats when document processing completes
CREATE TRIGGER IF NOT EXISTS update_user_stats_complete
AFTER UPDATE OF status ON documents
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    -- Parse metrics JSON and update stats
    UPDATE user_stats 
    SET grammar_fixes = grammar_fixes + COALESCE(json_extract(NEW.metrics, '$.grammar_fixes'), 0),
        clarity_improvements = clarity_improvements + COALESCE(json_extract(NEW.metrics, '$.clarity_improvements'), 0),
        tone_adjustments = tone_adjustments + COALESCE(json_extract(NEW.metrics, '$.tone_adjustments'), 0),
        formatting_changes = formatting_changes + COALESCE(json_extract(NEW.metrics, '$.formatting_changes'), 0),
        total_words = total_words + COALESCE(json_extract(NEW.metrics, '$.processed_word_count'), 0),
        last_processed = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id;
END;

-- Update subscription updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_subscription_timestamp
AFTER UPDATE ON user_subscriptions
BEGIN
    UPDATE user_subscriptions 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Update user max_documents when subscription changes
CREATE TRIGGER IF NOT EXISTS update_user_max_docs_on_subscription
AFTER INSERT ON user_subscriptions
BEGIN
    UPDATE users 
    SET max_documents = (SELECT max_documents FROM subscription_plans WHERE id = NEW.plan_id)
    WHERE id = NEW.user_id;
END;

CREATE TRIGGER IF NOT EXISTS update_user_max_docs_on_subscription_update
AFTER UPDATE OF plan_id ON user_subscriptions
BEGIN
    UPDATE users 
    SET max_documents = (SELECT max_documents FROM subscription_plans WHERE id = NEW.plan_id)
    WHERE id = NEW.user_id;
END;

-- Clean up expired sessions
CREATE TRIGGER IF NOT EXISTS cleanup_expired_sessions
AFTER INSERT ON user_sessions
BEGIN
    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP;
END;

-- Views for common queries

-- User dashboard view
CREATE VIEW IF NOT EXISTS user_dashboard AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    u.user_type,
    u.documents_count,
    u.max_documents,
    u.created_at as user_since,
    u.last_login,
    u.api_key,
    COALESCE(us.total_documents, 0) as total_documents_processed,
    COALESCE(us.grammar_fixes, 0) as total_grammar_fixes,
    COALESCE(us.clarity_improvements, 0) as total_clarity_improvements,
    COALESCE(us.tone_adjustments, 0) as total_tone_adjustments,
    COALESCE(us.formatting_changes, 0) as total_formatting_changes,
    COALESCE(us.total_words, 0) as total_words_processed,
    COALESCE(us.last_processed, u.created_at) as last_processed_date,
    (SELECT COUNT(*) FROM documents d WHERE d.user_id = u.id AND DATE(d.created_at) = DATE('now')) as documents_today,
    (SELECT status FROM user_subscriptions sub WHERE sub.user_id = u.id ORDER BY created_at DESC LIMIT 1) as subscription_status,
    (SELECT name FROM subscription_plans sp 
     JOIN user_subscriptions sub ON sp.id = sub.plan_id 
     WHERE sub.user_id = u.id ORDER BY sub.created_at DESC LIMIT 1) as subscription_plan
FROM users u
LEFT JOIN user_stats us ON u.id = us.user_id;

-- Recent documents view
CREATE VIEW IF NOT EXISTS recent_documents AS
SELECT 
    d.id,
    d.user_id,
    d.file_id,
    d.original_filename,
    d.mode,
    d.status,
    d.created_at,
    d.processed_at,
    u.name as user_name,
    u.email as user_email,
    COALESCE(json_extract(d.metrics, '$.processing_time'), 0) as processing_time_seconds,
    COALESCE(json_extract(d.metrics, '$.total_changes'), 0) as total_changes,
    COALESCE(json_extract(d.metrics, '$.grammar_fixes'), 0) as grammar_fixes,
    COALESCE(json_extract(d.metrics, '$.clarity_improvements'), 0) as clarity_improvements,
    COALESCE(json_extract(d.metrics, '$.tone_adjustments'), 0) as tone_adjustments,
    COALESCE(json_extract(d.metrics, '$.formatting_changes'), 0) as formatting_changes,
    COALESCE(json_extract(d.metrics, '$.improvement_percentage'), 0) as improvement_percentage
FROM documents d
JOIN users u ON d.user_id = u.id
ORDER BY d.created_at DESC;

-- System statistics view
CREATE VIEW IF NOT EXISTS system_statistics AS
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM users WHERE is_active = 1) as active_users,
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM documents WHERE DATE(created_at) = DATE('now')) as documents_today,
    (SELECT COUNT(*) FROM documents WHERE status = 'completed') as completed_documents,
    (SELECT COUNT(*) FROM documents WHERE status = 'processing') as processing_documents,
    (SELECT COUNT(*) FROM documents WHERE status = 'failed') as failed_documents,
    (SELECT COALESCE(SUM(COALESCE(json_extract(metrics, '$.processing_time'), 0)), 0) 
     FROM documents WHERE status = 'completed') as total_processing_time,
    (SELECT COALESCE(AVG(COALESCE(json_extract(metrics, '$.processing_time'), 0)), 0) 
     FROM documents WHERE status = 'completed') as avg_processing_time,
    (SELECT COALESCE(SUM(COALESCE(json_extract(metrics, '$.total_changes'), 0)), 0) 
     FROM documents WHERE status = 'completed') as total_changes_made,
    (SELECT COALESCE(AVG(COALESCE(json_extract(metrics, '$.improvement_percentage'), 0)), 0) 
     FROM documents WHERE status = 'completed') as avg_improvement_percentage;

-- User activity view
CREATE VIEW IF NOT EXISTS user_activity AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    COUNT(d.id) as total_documents,
    MAX(d.created_at) as last_upload,
    COUNT(CASE WHEN d.status = 'completed' THEN 1 END) as completed_documents,
    COUNT(CASE WHEN d.status = 'processing' THEN 1 END) as processing_documents,
    COUNT(CASE WHEN DATE(d.created_at) = DATE('now') THEN 1 END) as today_documents,
    COALESCE(SUM(COALESCE(json_extract(d.metrics, '$.total_changes'), 0)), 0) as total_changes,
    COALESCE(AVG(COALESCE(json_extract(d.metrics, '$.improvement_percentage'), 0)), 0) as avg_improvement
FROM users u
LEFT JOIN documents d ON u.id = d.user_id
GROUP BY u.id, u.name, u.email
ORDER BY total_documents DESC;

-- Document metrics view
CREATE VIEW IF NOT EXISTS document_metrics AS
SELECT 
    d.id,
    d.user_id,
    d.original_filename,
    d.mode,
    d.status,
    d.created_at,
    json_extract(d.metrics, '$.processing_time') as processing_time,
    json_extract(d.metrics, '$.total_changes') as total_changes,
    json_extract(d.metrics, '$.grammar_fixes') as grammar_fixes,
    json_extract(d.metrics, '$.clarity_improvements') as clarity_improvements,
    json_extract(d.metrics, '$.tone_adjustments') as tone_adjustments,
    json_extract(d.metrics, '$.formatting_changes') as formatting_changes,
    json_extract(d.metrics, '$.improvement_percentage') as improvement_percentage,
    json_extract(d.metrics, '$.original_word_count') as original_word_count,
    json_extract(d.metrics, '$.processed_word_count') as processed_word_count,
    u.name as user_name,
    u.email as user_email
FROM documents d
JOIN users u ON d.user_id = u.id
WHERE d.metrics IS NOT NULL AND d.status = 'completed';

-- Popular document modes view
CREATE VIEW IF NOT EXISTS popular_modes AS
SELECT 
    mode,
    COUNT(*) as document_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM documents), 2) as percentage
FROM documents
GROUP BY mode
ORDER BY document_count DESC;

-- API usage summary view
CREATE VIEW IF NOT EXISTS api_usage_summary AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    COUNT(au.id) as total_requests,
    COUNT(CASE WHEN DATE(au.timestamp) = DATE('now') THEN 1 END) as today_requests,
    COUNT(CASE WHEN au.timestamp >= datetime('now', '-1 hour') THEN 1 END) as hour_requests,
    AVG(au.response_time) as avg_response_time,
    MIN(au.timestamp) as first_request,
    MAX(au.timestamp) as last_request
FROM users u
LEFT JOIN api_usage au ON u.id = au.user_id
GROUP BY u.id, u.name, u.email;

-- Insert default subscription plans
INSERT OR IGNORE INTO subscription_plans (name, description, max_documents, price_monthly, price_yearly, features) VALUES
('free', 'Free Plan - Perfect for trying out ScholarFix', 5, 0.00, 0.00, '["Basic grammar checking", "Standard formatting", "5 documents per day", "Email support"]'),
('student', 'Student Plan - Academic excellence', 10, 4.99, 49.99, '["Advanced grammar checking", "Academic formatting", "10 documents per day", "Citation support", "Priority email support"]'),
('professional', 'Professional Plan - Business documents', 20, 9.99, 99.99, '["All Student features", "Professional formatting", "20 documents per day", "API access", "Priority support", "PDF export"]'),
('premium', 'Premium Plan - Unlimited refinement', 100, 19.99, 199.99, '["All Professional features", "Unlimited documents", "Advanced formatting options", "Team collaboration", "Dedicated support", "Custom templates"]'),
('enterprise', 'Enterprise Plan - For organizations', 1000, 99.99, 999.99, '["All Premium features", "Custom limits", "White-label options", "SLA guarantee", "Dedicated account manager", "Custom integrations"]');

-- Insert default admin user if not exists
INSERT OR IGNORE INTO users (email, name, password_hash, user_type, max_documents, api_key) 
VALUES ('admin@scholarfix.com', 'System Administrator', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', 1000, 'admin-' || lower(hex(randomblob(16))));

-- Insert test user if not exists
INSERT OR IGNORE INTO users (email, name, password_hash, user_type, max_documents, api_key) 
VALUES ('test@scholarfix.com', 'Test User', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'professional', 50, 'test-' || lower(hex(randomblob(16))));

-- Create system log for initialization
INSERT INTO system_logs (log_level, message, source, ip_address, user_agent) 
VALUES ('INFO', 'Database schema initialized successfully', 'database', '127.0.0.1', 'System/1.0');