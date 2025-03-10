# Spanda.AI RAG API Documentation

## Table of Contents
- [Health and Connection](#health-and-connection)
- [WebSocket Endpoints](#websocket-endpoints)
- [File Import](#file-import)
- [Configuration Management](#configuration-management)
- [Document Retrieval and Management](#document-retrieval-and-management)
- [Administration](#administration)
- [Suggestions Management](#suggestions-management)
- [Static Content](#static-content)

## Health and Connection

### GET /api/health
**Description:** Checks if the application is running and returns deployment information.

**Response:**
```json
{
  "message": "Alive!",
  "production": "Local|Demo|Custom",
  "gtag": "string",
  "deployments": {
    "WEAVIATE_URL_VERBA": "string",
    "WEAVIATE_API_KEY_VERBA": "string"
  },
  "default_deployment": "string"
}
```

### POST /api/connect
**Description:** Connects to the Verba backend.

**Request Body:**
```json
{
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  },
  "port": "string"
}
```

**Response:**
```json
{
  "connected": true,
  "error": "",
  "rag_config": {
    // RAG configuration object
  },
  "user_config": {
    // User configuration object
  },
  "theme": {
    // Current theme configuration
  },
  "themes": {
    // Available themes
  }
}
```

**Error Response:**
```json
{
  "connected": false,
  "error": "Error message",
  "rag_config": {},
  "theme": {},
  "themes": {}
}
```

## WebSocket Endpoints

### WS /ws/generate_stream
**Description:** Streams generated responses for queries.

**Request:**
```json
{
  "query": "string",
  "context": "string",
  "conversation": [
    {
      "type": "string",
      "content": "string"
    }
  ],
  "rag_config": {
    // RAG component configuration
  }
}
```

**Response Stream:**
Each chunk contains:
```json
{
  "message": "string",
  "finish_reason": "string|null",
  "full_text": "string" // Only in the final chunk
}
```

### WS /ws/import_files
**Description:** Handles file imports via WebSocket. Not available in Demo mode.

**Request:**
```json
{
  "chunk": "string",
  "isLastChunk": boolean,
  "total": integer,
  "fileID": "string",
  "order": integer,
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  },
  "rag_config": {
    // RAG configuration
  },
  "file_data": {
    // File metadata
  }
}
```

**Response:**
Status updates are sent as messages during the import process.

## File Import

### POST /api/import_file
**Description:** Alternative HTTP endpoint for file imports.

**Request Body:**
```json
{
  "fileID": "string",
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  },
  "rag_config": {
    // RAG configuration
  },
  "file_data": {
    // File metadata
  },
  "total": integer,
  "order": integer,
  "chunk": "string",
  "isLastChunk": boolean
}
```

**Success Response:**
```json
{
  "status": "success",
  "message": "File imported successfully."
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error message"
}
```

## Configuration Management

### POST /api/get_rag_config
**Description:** Retrieves RAG (Retrieval Augmented Generation) configuration.

**Request Body:**
```json
{
  "deployment": "Weaviate|Docker|Local|Custom",
  "url": "string",
  "key": "string"
}
```

**Response:**
```json
{
  "rag_config": {
    "Reader": {
      "selected": "string",
      "components": {
        // Component configurations
      }
    },
    "Chunker": {
      "selected": "string",
      "components": {
        // Component configurations
      }
    },
    "Embedder": {
      "selected": "string",
      "components": {
        // Component configurations
      }
    },
    "Retriever": {
      "selected": "string",
      "components": {
        // Component configurations
      }
    },
    "Generator": {
      "selected": "string",
      "components": {
        // Component configurations
      }
    }
  },
  "error": ""
}
```

### POST /api/set_rag_config
**Description:** Updates the RAG configuration. Not available in Demo mode.

**Request Body:**
```json
{
  "rag_config": {
    // Full RAG configuration object (see RAGConfig model)
  },
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "status": 200
}
```

**Error Response:**
```json
{
  "status": 400,
  "status_msg": "Error message"
}
```

### POST /api/get_user_config
**Description:** Retrieves user configuration.

**Request Body:**
```json
{
  "deployment": "Weaviate|Docker|Local|Custom",
  "url": "string",
  "key": "string"
}
```

**Response:**
```json
{
  "user_config": {
    // User configuration object
  },
  "error": ""
}
```

### POST /api/set_user_config
**Description:** Updates the user configuration. Not available in Demo mode.

**Request Body:**
```json
{
  "user_config": {
    // User configuration object
  },
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "status": 200,
  "status_msg": "User config updated"
}
```

**Error Response:**
```json
{
  "status": 400,
  "status_msg": "Error message"
}
```

### POST /api/get_theme_config
**Description:** Retrieves theme configuration.

**Request Body:**
```json
{
  "deployment": "Weaviate|Docker|Local|Custom",
  "url": "string",
  "key": "string"
}
```

**Response:**
```json
{
  "theme": {
    // Current theme configuration
  },
  "themes": {
    // Available themes
  },
  "error": ""
}
```

### POST /api/set_theme_config
**Description:** Updates the theme configuration. Not available in Demo mode.

**Request Body:**
```json
{
  "theme": {
    // Theme configuration
  },
  "themes": {
    // Available themes
  },
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "status": 200
}
```

**Error Response:**
```json
{
  "status": 400,
  "status_msg": "Error message"
}
```

## Document Retrieval and Management

### POST /api/query
**Description:** Retrieves chunks and context based on a query.

**Request Body:**
```json
{
  "query": "string",
  "RAG": {
    // RAG component configuration
  },
  "labels": ["string"],
  "documentFilter": [
    {
      "title": "string",
      "uuid": "string"
    }
  ],
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "error": "",
  "documents": [
    // Document objects
  ],
  "context": "string"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "documents": [],
  "context": ""
}
```

### POST /api/get_document
**Description:** Retrieves a specific document by UUID.

**Request Body:**
```json
{
  "uuid": "string",
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "error": "",
  "document": {
    "title": "string",
    "extension": "string",
    "fileSize": number,
    "labels": ["string"],
    "source": "string",
    "meta": {},
    "metadata": {},
    "content": ""
  }
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "document": null
}
```

### POST /api/get_datacount
**Description:** Retrieves document count statistics.

**Request Body:**
```json
{
  "embedding_model": "string",
  "documentFilter": [
    {
      "title": "string",
      "uuid": "string"
    }
  ],
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Response:**
```json
{
  "datacount": number
}
```

### POST /api/get_labels
**Description:** Retrieves all available document labels.

**Request Body:**
```json
{
  "deployment": "Weaviate|Docker|Local|Custom",
  "url": "string",
  "key": "string"
}
```

**Response:**
```json
{
  "labels": ["string"]
}
```

### POST /api/get_content
**Description:** Retrieves document content.

**Request Body:**
```json
{
  "uuid": "string",
  "page": number,
  "chunkScores": [
    {
      "uuid": "string",
      "score": number,
      "chunk_id": number,
      "embedder": "string"
    }
  ],
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "error": "",
  "content": "string",
  "maxPage": number
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "document": null
}
```

### POST /api/get_vectors
**Description:** Retrieves vector representations for a document.

**Request Body:**
```json
{
  "uuid": "string",
  "showAll": boolean,
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "error": "",
  "vector_groups": [
    // Vector group objects
  ]
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "payload": {
    "embedder": "None",
    "vectors": []
  }
}
```

### POST /api/get_chunks
**Description:** Retrieves chunks from a document with pagination.

**Request Body:**
```json
{
  "uuid": "string",
  "page": number,
  "pageSize": number,
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "error": "",
  "chunks": [
    // Chunk objects
  ]
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "chunks": null
}
```

### POST /api/get_chunk
**Description:** Retrieves a specific chunk by UUID and embedder.

**Request Body:**
```json
{
  "uuid": "string",
  "embedder": "string",
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "error": "",
  "chunk": {
    // Chunk object
  }
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "chunk": null
}
```

### POST /api/get_all_documents
**Description:** Searches and retrieves documents with pagination.

**Request Body:**
```json
{
  "query": "string",
  "labels": ["string"],
  "page": number,
  "pageSize": number,
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "documents": [
    {
      "title": "string",
      "extension": "string",
      "fileSize": number,
      "labels": ["string"],
      "source": "string",
      "meta": {}
    }
  ],
  "labels": ["string"],
  "error": "",
  "totalDocuments": number
}
```

**Error Response:**
```json
{
  "documents": [],
  "label": [],
  "error": "Error message",
  "totalDocuments": 0
}
```

### POST /api/delete_document
**Description:** Deletes a specific document. Not available in Demo mode.

**Request Body:**
```json
{
  "uuid": "string",
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{}
```

**Error Response:**
Status code 400 with empty body.

## Administration

### POST /api/reset
**Description:** Resets the Verba application data. Not available in Demo mode.

**Request Body:**
```json
{
  "resetMode": "ALL|DOCUMENTS|CONFIG|SUGGESTIONS",
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Reset Modes:**
- `ALL`: Deletes all data
- `DOCUMENTS`: Deletes all documents
- `CONFIG`: Deletes all configurations
- `SUGGESTIONS`: Deletes all suggestions

**Success Response:**
```json
{}
```

**Error Response:**
Status code 500 with empty body.

### POST /api/get_meta
**Description:** Retrieves metadata about Weaviate node and collections.

**Request Body:**
```json
{
  "deployment": "Weaviate|Docker|Local|Custom",
  "url": "string",
  "key": "string"
}
```

**Success Response:**
```json
{
  "error": "",
  "node_payload": {
    // Node metadata
  },
  "collection_payload": {
    // Collection metadata
  }
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "node_payload": {},
  "collection_payload": {}
}
```

## Suggestions Management

### POST /api/get_suggestions
**Description:** Retrieves query suggestions based on a partial query.

**Request Body:**
```json
{
  "query": "string",
  "limit": number,
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Response:**
```json
{
  "suggestions": [
    // Suggestion objects
  ]
}
```

### POST /api/get_all_suggestions
**Description:** Retrieves all suggestions with pagination.

**Request Body:**
```json
{
  "page": number,
  "pageSize": number,
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Response:**
```json
{
  "suggestions": [
    // Suggestion objects
  ],
  "total_count": number
}
```

### POST /api/delete_suggestion
**Description:** Deletes a specific suggestion.

**Request Body:**
```json
{
  "uuid": "string",
  "credentials": {
    "deployment": "Weaviate|Docker|Local|Custom",
    "url": "string",
    "key": "string"
  }
}
```

**Success Response:**
```json
{
  "status": 200
}
```

**Error Response:**
```json
{
  "status": 400
}
```

## Static Content

### GET /
**Description:** Serves the main frontend application.
**Response:** HTML content of the main application page

### GET /static/_next/*
**Description:** Serves Next.js assets

### GET /static/*
**Description:** Serves other static files