```mermaid
flowchart TB
    User[User] --> WebUI[Web Interface\n<i>app.py</i>]
    User --> CLI[CLI Interface\n<i>cli.py</i>]
    User --> ClientApp[Client Application]
    
    ClientApp -->|HTTP Requests| API[REST API\n<i>api.py</i>]
    WebUI --> Engine
    CLI --> Engine
    API --> Engine
    
    subgraph Core["InsolvencyBot Core"]
        Engine[InsolvencyBot Engine\n<i>insolvency_bot.py</i>] --> Prompt[Prompt Engineering]
        Prompt --> OpenAI[OpenAI API]
        OpenAI --> ResponseProc[Response Processing]
        ResponseProc --> RefExtract[Reference Extraction]
    end
    
    Engine --> StructuredResponse[Structured Response\n<code>{response, legislation, cases, forms}</code>]
    
    StructuredResponse --> WebUI
    StructuredResponse --> CLI
    StructuredResponse --> API
    API -->|JSON Response| ClientApp
    StructuredResponse --> CLI
    StructuredResponse --> API
    
    Benchmark[Benchmarking\n<i>benchmark.py</i>] -->|Performance Metrics| Engine
    
    subgraph Data
        TrainingData[Training Data]
        TestData[Test Data]
        Evaluation[Evaluation Scripts]
    end
    
    Evaluation --> Engine
    
    style Core fill:#f9f9f9,stroke:#333,stroke-width:2px
    style User fill:#d4f1f9,stroke:#333,stroke-width:1px
    style StructuredResponse fill:#e1f5c4,stroke:#333,stroke-width:1px
    style Data fill:#fdf7e3,stroke:#333,stroke-width:2px
```

## Sequence Diagram: Question Processing

```mermaid
sequenceDiagram
    participant User
    participant Interface as User Interface (CLI/Web/API)
    participant Bot as InsolvencyBot Engine
    participant LLM as OpenAI LLM
    participant Extractor as Reference Extractor
    
    User->>Interface: Submit question
    Interface->>Bot: Process question
    Bot->>LLM: Send prompt
    LLM->>Bot: Return response
    Bot->>Extractor: Extract references
    Extractor->>Bot: Return structured references
    Bot->>Interface: Return structured response
    Interface->>User: Display answer with references
```

## API Architecture

```mermaid
flowchart TB
    subgraph "API Endpoints"
        ROOT[GET /\nAPI Info]
        MODELS[GET /models\nAvailable Models]
        ASK[POST /ask\nProcess Questions]
    end
    
    subgraph "Middleware"
        AUTH[Authentication\nAPI Key Validation]
        CORS[CORS Handling]
        ERROR[Error Handling]
    end
    
    subgraph "Core Services"
        BOT[InsolvencyBot Engine]
    end
    
    ROOT --> AUTH
    MODELS --> AUTH
    ASK --> AUTH
    
    AUTH --> CORS
    CORS --> ERROR
    ERROR --> BOT
    
    BOT --> OpenAI[OpenAI API]
    
    style ASK fill:#bbf,stroke:#333,stroke-width:2px
    style BOT fill:#f9f,stroke:#333,stroke-width:2px
```

## Deployment Architecture

```mermaid
flowchart TB
    subgraph "Client Applications"
        WEB_CLIENT[Web Browsers]
        API_CLIENT[API Clients]
        CLI_CLIENT[Command Line]
    end
    
    subgraph "Docker Containers"
        API_CONTAINER[API Service\nPort 8000]
        WEB_CONTAINER[Web Service\nPort 5000]
    end
    
    subgraph "Dependencies"
        OPENAI[OpenAI API]
    end
    
    WEB_CLIENT --> WEB_CONTAINER
    API_CLIENT --> API_CONTAINER
    CLI_CLIENT --> CLI[CLI Tool]
    
    WEB_CONTAINER --> API_CONTAINER
    API_CONTAINER --> OPENAI
    CLI --> OPENAI
    
    style API_CONTAINER fill:#bbf,stroke:#333,stroke-width:2px
```
