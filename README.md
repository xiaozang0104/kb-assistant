# kb-assistant

A knowledge-base assistant web application. Users can upload documents,
ask questions, and get answers from a local knowledge base powered by a
RAG pipeline and an AI agent. (Under development.)

## Progress

- [x] Week 1: database schema (users, documents, chunks, conversations, messages)
- [x] Week 2: web backend (planned)

## API

- `GET /users` - list all users
- `GET /documents` - list all documents
- `GET /documents/{id}` - get one document
- `POST /documents` - create a document
- `DELETE /documents/{id}` - delete a document

## Structure

- `db/` : SQL schema, seed data, and queries