
CREATE TABLE generated_summaries (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    summary_uuid TEXT NOT NULL ,
    summ_id TEXT NOT NULL, 
    system_id TEXT NOT NULL, 
    summary TEXT NOT NULL
);
CREATE TABLE source_article (
    uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    summary_uuid TEXT NOT NULL,
    article_id TEXT NOT NULL,
    article TEXT
);
CREATE TABLE label (
    summary_uuid INTEGER PRIMARY KEY AUTOINCREMENT, 
    summary_uuid TEXT NOT NULL,
    label_type TEXT NOT NULL,
    score INTEGER NOT NULL
);