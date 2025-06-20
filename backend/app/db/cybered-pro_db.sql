-- cybered-pro_db.sql
-- Complete SQL statements to create and populate the CyberEd Pro database

-- Create the database
-- CREATE DATABASE cybered_pro;

-- Connect to the database
-- \c cybered_pro

-- Function for automatically updating timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Users Table
CREATE TABLE users (
                       id SERIAL PRIMARY KEY,
                       email VARCHAR(255) UNIQUE NOT NULL,
                       first_name VARCHAR(100) NOT NULL,
                       last_name VARCHAR(100) NOT NULL,
                       hashed_password VARCHAR(255) NOT NULL,
                       role VARCHAR(20) NOT NULL DEFAULT 'student', -- student, instructor, admin
                       is_active BOOLEAN NOT NULL DEFAULT TRUE,
                       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                       updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster email lookups
CREATE INDEX idx_users_email ON users(email);

-- Courses Table
CREATE TABLE courses (
                         id SERIAL PRIMARY KEY,
                         title VARCHAR(255) NOT NULL,
                         description TEXT,
                         instructor_id INTEGER NOT NULL REFERENCES users(id),
                         certification_type VARCHAR(100), -- Security+, CEH, CISSP, etc.
                         difficulty_level VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced
                         estimated_duration INTEGER, -- in hours
                         is_published BOOLEAN NOT NULL DEFAULT FALSE,
                         created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                         updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_certification ON courses(certification_type);
CREATE INDEX idx_courses_difficulty ON courses(difficulty_level);

-- Modules Table
CREATE TABLE modules (
                         id SERIAL PRIMARY KEY,
                         course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                         title VARCHAR(255) NOT NULL,
                         description TEXT,
                         order_index INTEGER NOT NULL,
                         created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                         updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_modules_course ON modules(course_id);
CREATE INDEX idx_modules_order ON modules(course_id, order_index);

-- Lessons Table
CREATE TABLE lessons (
                         id SERIAL PRIMARY KEY,
                         module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
                         title VARCHAR(255) NOT NULL,
                         content_type VARCHAR(50) NOT NULL, -- text, video, interactive
                         content TEXT NOT NULL,
                         order_index INTEGER NOT NULL,
                         created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                         updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_lessons_module ON lessons(module_id);
CREATE INDEX idx_lessons_order ON lessons(module_id, order_index);

-- Enrollments Table
CREATE TABLE enrollments (
                             id SERIAL PRIMARY KEY,
                             user_id INTEGER NOT NULL REFERENCES users(id),
                             course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                             status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, completed, withdrawn
                             progress FLOAT NOT NULL DEFAULT 0.0, -- 0 to 100 percent
                             enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                             completed_at TIMESTAMP WITH TIME ZONE,

    -- Ensure a user can only be enrolled once in a course
                             CONSTRAINT unique_user_course UNIQUE (user_id, course_id)
);

-- Indexes
CREATE INDEX idx_enrollments_user ON enrollments(user_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);

-- Assessments Table
CREATE TABLE assessments (
                             id SERIAL PRIMARY KEY,
                             course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                             module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
                             title VARCHAR(255) NOT NULL,
                             description TEXT,
                             time_limit_minutes INTEGER,
                             passing_score FLOAT NOT NULL DEFAULT 70.0,
                             is_published BOOLEAN NOT NULL DEFAULT FALSE,
                             created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                             updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_assessments_course ON assessments(course_id);
CREATE INDEX idx_assessments_module ON assessments(module_id);

-- Questions Table
CREATE TABLE questions (
                           id SERIAL PRIMARY KEY,
                           assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
                           question_text TEXT NOT NULL,
                           question_type VARCHAR(20) NOT NULL, -- mcq, true_false, short_answer
                           points FLOAT NOT NULL DEFAULT 1.0,
                           created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                           updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_questions_assessment ON questions(assessment_id);

-- Answers Table
CREATE TABLE answers (
                         id SERIAL PRIMARY KEY,
                         question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
                         answer_text TEXT NOT NULL,
                         is_correct BOOLEAN NOT NULL DEFAULT FALSE,
                         explanation TEXT,
                         created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                         updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_answers_question ON answers(question_id);

-- User Assessments Table
CREATE TABLE user_assessments (
                                  id SERIAL PRIMARY KEY,
                                  user_id INTEGER NOT NULL REFERENCES users(id),
                                  assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
                                  score FLOAT,
                                  start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                                  end_time TIMESTAMP WITH TIME ZONE,
                                  status VARCHAR(20) NOT NULL DEFAULT 'in_progress' -- in_progress, completed
);

-- Indexes
CREATE INDEX idx_user_assessments_user ON user_assessments(user_id);
CREATE INDEX idx_user_assessments_assessment ON user_assessments(assessment_id);
CREATE INDEX idx_user_assessments_status ON user_assessments(status);

-- User Answers Table
CREATE TABLE user_answers (
                              id SERIAL PRIMARY KEY,
                              user_assessment_id INTEGER NOT NULL REFERENCES user_assessments(id) ON DELETE CASCADE,
                              question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
                              answer_id INTEGER REFERENCES answers(id) ON DELETE SET NULL,
                              text_answer TEXT,
                              is_correct BOOLEAN,
                              points_earned FLOAT
);

-- Indexes
CREATE INDEX idx_user_answers_assessment ON user_answers(user_assessment_id);
CREATE INDEX idx_user_answers_question ON user_answers(question_id);

-- User Lesson Progress Table
CREATE TABLE user_lesson_progress (
                                      id SERIAL PRIMARY KEY,
                                      user_id INTEGER NOT NULL REFERENCES users(id),
                                      lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                                      completed BOOLEAN NOT NULL DEFAULT FALSE,
                                      last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique user-lesson combination
                                      CONSTRAINT unique_user_lesson UNIQUE (user_id, lesson_id)
);

-- Indexes
CREATE INDEX idx_lesson_progress_user ON user_lesson_progress(user_id);
CREATE INDEX idx_lesson_progress_lesson ON user_lesson_progress(lesson_id);

-- User Notes Table
CREATE TABLE user_notes (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL REFERENCES users(id),
                            lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                            content TEXT NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notes_user ON user_notes(user_id);
CREATE INDEX idx_notes_lesson ON user_notes(lesson_id);

-- Bookmarks Table
CREATE TABLE bookmarks (
                           id SERIAL PRIMARY KEY,
                           user_id INTEGER NOT NULL REFERENCES users(id),
                           lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                           created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique user-lesson bookmark
                           CONSTRAINT unique_user_bookmark UNIQUE (user_id, lesson_id)
);

-- Indexes
CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);

-- Forum Topics Table
CREATE TABLE forum_topics (
                              id SERIAL PRIMARY KEY,
                              course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                              title VARCHAR(255) NOT NULL,
                              content TEXT NOT NULL,
                              user_id INTEGER NOT NULL REFERENCES users(id),
                              created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                              updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_forum_topics_course ON forum_topics(course_id);
CREATE INDEX idx_forum_topics_user ON forum_topics(user_id);

-- Forum Replies Table
CREATE TABLE forum_replies (
                               id SERIAL PRIMARY KEY,
                               topic_id INTEGER NOT NULL REFERENCES forum_topics(id) ON DELETE CASCADE,
                               content TEXT NOT NULL,
                               user_id INTEGER NOT NULL REFERENCES users(id),
                               created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_forum_replies_topic ON forum_replies(topic_id);
CREATE INDEX idx_forum_replies_user ON forum_replies(user_id);

-- Certifications Table
CREATE TABLE certifications (
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(100) NOT NULL,
                                description TEXT,
                                requirements TEXT,
                                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Certifications Table
CREATE TABLE user_certifications (
                                     id SERIAL PRIMARY KEY,
                                     user_id INTEGER NOT NULL REFERENCES users(id),
                                     certification_id INTEGER NOT NULL REFERENCES certifications(id) ON DELETE CASCADE,
                                     issue_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                                     expiry_date TIMESTAMP WITH TIME ZONE,
                                     certificate_url VARCHAR(255),

    -- Ensure uniqueness
                                     CONSTRAINT unique_user_certification UNIQUE (user_id, certification_id)
);

-- Indexes
CREATE INDEX idx_user_certifications_user ON user_certifications(user_id);
CREATE INDEX idx_user_certifications_cert ON user_certifications(certification_id);

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_courses_modtime
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_modules_modtime
    BEFORE UPDATE ON modules
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_lessons_modtime
    BEFORE UPDATE ON lessons
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_assessments_modtime
    BEFORE UPDATE ON assessments
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_questions_modtime
    BEFORE UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_answers_modtime
    BEFORE UPDATE ON answers
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_user_notes_modtime
    BEFORE UPDATE ON user_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_forum_topics_modtime
    BEFORE UPDATE ON forum_topics
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_forum_replies_modtime
    BEFORE UPDATE ON forum_replies
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Insert sample data

-- Create admin user
INSERT INTO users (email, first_name, last_name, hashed_password, role)
VALUES (
           'admin@cyberedpro.com',
           'Admin',
           'User',
           '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- 'password'
           'admin'
       );

-- Create instructor user
INSERT INTO users (email, first_name, last_name, hashed_password, role)
VALUES (
           'instructor@cyberedpro.com',
           'Jane',
           'Smith',
           '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- 'password'
           'instructor'
       );

-- Create student user
INSERT INTO users (email, first_name, last_name, hashed_password, role)
VALUES (
           'student@cyberedpro.com',
           'John',
           'Doe',
           '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- 'password'
           'student'
       );

-- Create sample courses
INSERT INTO courses (title, description, instructor_id, certification_type, difficulty_level, estimated_duration, is_published)
VALUES (
           'CompTIA Security+ Certification Prep',
           'Comprehensive preparation for the CompTIA Security+ certification exam. This course covers all domains required for the certification.',
           2, -- instructor user id
           'Security+',
           'intermediate',
           40,
           TRUE
       );

INSERT INTO courses (title, description, instructor_id, certification_type, difficulty_level, estimated_duration, is_published)
VALUES (
           'Certified Ethical Hacker (CEH) Training',
           'Learn ethical hacking techniques and methodologies to secure systems against cyber threats. Prepare for the CEH certification.',
           2, -- instructor user id
           'CEH',
           'advanced',
           60,
           TRUE
       );

INSERT INTO courses (title, description, instructor_id, certification_type, difficulty_level, estimated_duration, is_published)
VALUES (
           'CISSP Certification Training',
           'Prepare for the Certified Information Systems Security Professional exam with comprehensive coverage of all eight domains.',
           2, -- instructor user id
           'CISSP',
           'advanced',
           80,
           TRUE
       );

-- Create sample modules
INSERT INTO modules (course_id, title, description, order_index)
VALUES (
           1, -- Security+ course
           'Introduction to Security Fundamentals',
           'Learn the basic concepts and principles of information security.',
           1
       );

INSERT INTO modules (course_id, title, description, order_index)
VALUES (
           1, -- Security+ course
           'Network Security',
           'Understanding network security principles, protocols, and implementation.',
           2
       );

INSERT INTO modules (course_id, title, description, order_index)
VALUES (
           1, -- Security+ course
           'Threats and Vulnerabilities',
           'Identifying and analyzing different types of security threats and vulnerabilities.',
           3
       );

INSERT INTO modules (course_id, title, description, order_index)
VALUES (
           2, -- CEH course
           'Ethical Hacking Basics',
           'Introduction to ethical hacking concepts and methodologies.',
           1
       );

INSERT INTO modules (course_id, title, description, order_index)
VALUES (
           2, -- CEH course
           'Reconnaissance Techniques',
           'Learn various information gathering and footprinting techniques.',
           2
       );

-- Create sample lessons
INSERT INTO lessons (module_id, title, content_type, content, order_index)
VALUES (
           1, -- Introduction module
           'What is Information Security?',
           'text',
           'Information security is the practice of protecting information by mitigating information risks. It includes protecting information from unauthorized access, use, disclosure, disruption, modification, or destruction. This lesson introduces the fundamental concepts of information security and why it is important in today''s digital world.',
           1
       );

INSERT INTO lessons (module_id, title, content_type, content, order_index)
VALUES (
           1, -- Introduction module
           'The CIA Triad',
           'text',
           'The CIA triad (Confidentiality, Integrity, and Availability) is a model designed to guide policies for information security within an organization. This lesson explains each component of the triad and how they work together to ensure comprehensive security.',
           2
       );

INSERT INTO lessons (module_id, title, content_type, content, order_index)
VALUES (
           1, -- Introduction module
           'Security Controls Overview',
           'text',
           'Security controls are safeguards or countermeasures to avoid, detect, counteract, or minimize security risks. This lesson covers the different types of security controls including preventive, detective, and corrective controls.',
           3
       );

INSERT INTO lessons (module_id, title, content_type, content, order_index)
VALUES (
           2, -- Network Security module
           'Network Protocols and Vulnerabilities',
           'text',
           'This lesson covers common network protocols and their associated security vulnerabilities. You will learn about TCP/IP, UDP, ICMP and how they can be exploited if not properly secured.',
           1
       );

INSERT INTO lessons (module_id, title, content_type, content, order_index)
VALUES (
           2, -- Network Security module
           'Secure Network Architecture',
           'text',
           'Building a secure network requires careful planning and implementation. This lesson covers defense in depth, network segmentation, and secure network devices.',
           2
       );

-- Create sample enrollment
INSERT INTO enrollments (user_id, course_id, status, progress)
VALUES (
           3, -- student user id
           1, -- Security+ course
           'active',
           0.0
       );

INSERT INTO enrollments (user_id, course_id, status, progress)
VALUES (
           3, -- student user id
           2, -- CEH course
           'active',
           0.0
       );

-- Create sample assessment
INSERT INTO assessments (course_id, module_id, title, description, time_limit_minutes, passing_score, is_published)
VALUES (
           1, -- Security+ course
           1, -- Introduction module
           'Security Fundamentals Quiz',
           'Test your understanding of basic security concepts and principles.',
           30,
           70.0,
           TRUE
       );

INSERT INTO assessments (course_id, module_id, title, description, time_limit_minutes, passing_score, is_published)
VALUES (
           1, -- Security+ course
           2, -- Network Security module
           'Network Security Assessment',
           'Evaluate your knowledge of network security protocols and implementation.',
           45,
           70.0,
           TRUE
       );

-- Create sample questions
INSERT INTO questions (assessment_id, question_text, question_type, points)
VALUES (
           1, -- Security Fundamentals Quiz
           'Which of the following is NOT a component of the CIA triad?',
           'mcq',
           1.0
       );

INSERT INTO questions (assessment_id, question_text, question_type, points)
VALUES (
           1, -- Security Fundamentals Quiz
           'True or False: Physical security controls are an important part of an organization''s overall security strategy.',
           'true_false',
           1.0
       );

INSERT INTO questions (assessment_id, question_text, question_type, points)
VALUES (
           1, -- Security Fundamentals Quiz
           'Explain the principle of least privilege and provide an example of its implementation.',
           'short_answer',
           2.0
       );

-- Create sample answers
INSERT INTO answers (question_id, answer_text, is_correct, explanation)
VALUES (
           1, -- question id
           'Confidentiality',
           FALSE,
           'Confidentiality is one of the three components of the CIA triad.'
       );

INSERT INTO answers (question_id, answer_text, is_correct, explanation)
VALUES (
           1, -- question id
           'Integrity',
           FALSE,
           'Integrity is one of the three components of the CIA triad.'
       );

INSERT INTO answers (question_id, answer_text, is_correct, explanation)
VALUES (
           1, -- question id
           'Authentication',
           TRUE,
           'Authentication is not part of the CIA triad. The three components are Confidentiality, Integrity, and Availability.'
       );

INSERT INTO answers (question_id, answer_text, is_correct, explanation)
VALUES (
           1, -- question id
           'Availability',
           FALSE,
           'Availability is one of the three components of the CIA triad.'
       );

INSERT INTO answers (question_id, answer_text, is_correct, explanation)
VALUES (
           2, -- true/false question
           'True',
           TRUE,
           'Physical security controls are essential for protecting assets from unauthorized physical access, damage, or theft, which is a crucial part of a comprehensive security strategy.'
       );

INSERT INTO answers (question_id, answer_text, is_correct, explanation)
VALUES (
           2, -- true/false question
           'False',
           FALSE,
           'This is incorrect. Physical security is a vital layer in defense in depth.'
       );

-- Create forum topics
INSERT INTO forum_topics (course_id, title, content, user_id)
VALUES (
           1, -- Security+ course
           'Study Group for Security+ Exam',
           'I''m planning to take the Security+ exam next month. Would anyone be interested in forming a study group to prepare together?',
           3  -- student user
       );

INSERT INTO forum_replies (topic_id, content, user_id)
VALUES (
           1, -- topic id
           'I''m also preparing for the exam. A study group sounds like a great idea!',
           3  -- student user
       );

INSERT INTO forum_replies (topic_id, content, user_id)
VALUES (
           1, -- topic id
           'As your instructor, I''d be happy to provide some guidance for your study group. Let me know what topics you find most challenging.',
           2  -- instructor user
       );

-- Create certifications
INSERT INTO certifications (name, description, requirements)
VALUES (
           'CompTIA Security+',
           'CompTIA Security+ is a global certification that validates the baseline skills necessary to perform core security functions and pursue an IT security career.',
           'Pass the Security+ SY0-601 exam with a score of 750 or higher (on a scale of 100-900).'
       );

INSERT INTO certifications (name, description, requirements)
VALUES (
           'Certified Ethical Hacker (CEH)',
           'The CEH credential certifies individuals in the specific network security discipline of Ethical Hacking from a vendor-neutral perspective.',
           'Pass the CEH exam with a score of 70% or higher.'
       );

INSERT INTO certifications (name, description, requirements)
VALUES (
           'CISSP',
           'The CISSP certification is ideal for security professionals who develop policies and procedures in information security.',
           'Have at least 5 years of cumulative, paid work experience in 2 or more of the 8 domains. Pass the CISSP exam with a scaled score of 700 points or greater.'
       );

-- Add some user progress data
INSERT INTO user_lesson_progress (user_id, lesson_id, completed)
VALUES (
           3, -- student user
           1, -- first lesson
           TRUE
       );

INSERT INTO user_lesson_progress (user_id, lesson_id, completed)
VALUES (
           3, -- student user
           2, -- second lesson
           TRUE
       );

INSERT INTO user_lesson_progress (user_id, lesson_id, completed)
VALUES (
           3, -- student user
           3, -- third lesson
           FALSE
       );

-- Add a bookmark
INSERT INTO bookmarks (user_id, lesson_id)
VALUES (
           3, -- student user
           2  -- second lesson
       );

-- Add a note
INSERT INTO user_notes (user_id, lesson_id, content)
VALUES (
           3, -- student user
           2, -- second lesson
           'The CIA triad seems to be a fundamental concept in security. Need to make sure I understand each component thoroughly.'
       );

-- Update course progress based on completed lessons
UPDATE enrollments
SET progress = 66.7 -- 2 out of 3 lessons completed
WHERE user_id = 3 AND course_id = 1;