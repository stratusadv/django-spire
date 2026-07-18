from __future__ import annotations

from test_project.app.comment.seeding.seeder import CommentExampleSeeder


comment_example = CommentExampleSeeder(count=10)

comment_example.seed_database()
