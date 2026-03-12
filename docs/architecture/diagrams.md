# Architecture Diagrams

This document contains visual diagrams that illustrate the architecture and data flows of the project.

---

## Class Diagram: API Layer

```mermaid
classDiagram
    class SatelliteImageDownloader {
        -api: SatelliteAPI
        -verbose: int
        +__init__(api, verbose)
        +search(filters) SearchResults
        +bulk_search(filters) SearchResults
        +bulk_download(images, outdir) List~str~
    }

    class SatelliteAPI {
        <<abstract>>
        #username: str
        #password: str
        +__init__(username, password)
        +search(filters)* SearchResults
        +download(image_id, outname, verbose)* str
        +bulk_search(filters) SearchResults
    }

    class ODataAPI {
        +SEARCH_URL: str
        +DOWNLOAD_URL: str
        +TOKEN_URL: str
        +search(filters) SearchResults
        +download(image_id, outname, verbose) str
        -__get_token() str
        -__prepare_query(filters) dict
        -__prepare_search_results(collection, images) SearchResults
    }

    class USGSAPI {
        +API_URL: str
        +LOGIN_ENDPOINT: str
        +SEARCH_ENDPOINT: str
        +DOWNLOAD_REQUEST_ENDPOINT: str
        +DOWNLOAD_OPTIONS_ENDPOINT: str
        -api_key: dict
        +search(filters) SearchResults
        +download(image_id, outname, verbose) str
        -__login() None
        -__prepare_query(filters) str
        -__request_download_metadata(collection, scenes) dict
    }

    SatelliteImageDownloader --> SatelliteAPI : uses
    SatelliteAPI <|-- ODataAPI : implements
    SatelliteAPI <|-- USGSAPI : implements
```

---

## Class Diagram: Data Types

```mermaid
classDiagram
    class SearchFilters {
        <<dataclass>>
        +collection: str
        +start_date: str
        +end_date: str
        +processing_level: str
        +geometry: str
        +tile_id: str
        +contains: List~str~
        +is_set(value) bool
    }

    class SatelliteImage {
        <<dataclass>>
        +uuid: str
        +date: str
        +sensor: str
        +brother: str
        +identifier: str
        +filename: str
        +tile: str
    }

    class COLLECTIONS {
        <<enumeration>>
        SENTINEL_2
        SENTINEL_3
        LANDSAT_8
    }

    class SearchResults {
        <<type alias>>
        Dict~str, SatelliteImage~
    }

    SearchResults ..> SatelliteImage : contains
    SearchFilters ..> COLLECTIONS : uses
```

---

## Component Diagram: Request Flow

```mermaid
graph TB
    subgraph "Presentation Layer"
        USER[User/Client]
    end

    subgraph "Service Layer"
        DOWNLOADER[SatelliteImageDownloader]
    end

    subgraph "Abstraction Layer"
        API[SatelliteAPI]
    end

    subgraph "API Implementations"
        ODATA[ODataAPI]
        USGS[USGSAPI]
    end

    subgraph "External Providers"
        COPERNICUS[(Copernicus Data Space)]
        EARTHEXPLORER[(USGS Earth Explorer)]
    end

    USER --> DOWNLOADER
    DOWNLOADER --> API
    API --> ODATA
    API --> USGS
    ODATA <--> COPERNICUS
    USGS <--> EARTHEXPLORER

    style USER fill:#e1f5ff
    style DOWNLOADER fill:#b3e5fc
    style API fill:#81d4fa
    style ODATA fill:#4fc3f7
    style USGS fill:#4fc3f7
    style COPERNICUS fill:#f8bbd0
    style EARTHEXPLORER fill:#f8bbd0
```

---

## Component Diagram: Data & Factories

```mermaid
graph TB
    subgraph "API Implementations"
        ODATA[ODataAPI]
        USGS[USGSAPI]
    end

    subgraph "Factories"
        FACTORY[get_satellite_image]
        S2[get_sentinel2]
        S3[get_sentinel3]
        L8[get_landsat_8]
    end

    subgraph "Data Layer"
        FILTERS[SearchFilters]
        IMAGE[SatelliteImage]
        RESULTS[SearchResults]
        ENUMS[COLLECTIONS]
    end

    ODATA --> FACTORY
    USGS --> FACTORY
    FACTORY --> S2
    FACTORY --> S3
    FACTORY --> L8
    S2 -.-> IMAGE
    S3 -.-> IMAGE
    L8 -.-> IMAGE
    FILTERS -.-> ENUMS
    RESULTS -.-> IMAGE

    style ODATA fill:#4fc3f7
    style USGS fill:#4fc3f7
    style FACTORY fill:#fff9c4
    style IMAGE fill:#c8e6c9
    style RESULTS fill:#c8e6c9
    style FILTERS fill:#c8e6c9
    style ENUMS fill:#f8bbd0
```

---

## Image Search Flow

```mermaid
sequenceDiagram
    actor User
    participant Downloader as SatelliteImageDownloader
    participant API as SatelliteAPI
    participant Impl as ODataAPI/USGSAPI
    participant Provider as External Provider
    participant Factory as get_satellite_image()

    User->>Downloader: search(filters)
    activate Downloader

    Downloader->>API: search(filters)
    activate API

    API->>Impl: search(filters)
    activate Impl

    Impl->>Impl: Authenticate
    Note over Impl: OAuth2 or<br/>API Token

    Impl->>Impl: Prepare query
    Note over Impl: OData or<br/>JSON REST

    Impl->>Provider: HTTP Request
    activate Provider
    Provider-->>Impl: JSON/XML Response
    deactivate Provider

    loop For each image
        Impl->>Factory: get_satellite_image(collection, data)
        activate Factory
        Factory->>Factory: Identify collection
        Factory->>Factory: Parse metadata
        Factory-->>Impl: SatelliteImage
        deactivate Factory
    end

    Impl-->>API: SearchResults
    deactivate Impl

    API-->>Downloader: SearchResults
    deactivate API

    Downloader-->>User: SearchResults
    deactivate Downloader
```

---

## Image Download Flow

```mermaid
sequenceDiagram
    actor User
    participant Downloader as SatelliteImageDownloader
    participant API as SatelliteAPI
    participant Impl as ODataAPI/USGSAPI
    participant Provider as External Provider
    participant FS as File System

    User->>Downloader: bulk_download(images, outdir)
    activate Downloader

    Downloader->>FS: Create directory
    FS-->>Downloader: OK

    loop For each image
        Downloader->>API: download(image_id, filepath, verbose)
        activate API

        API->>Impl: download(image_id, filepath, verbose)
        activate Impl

        Impl->>Impl: Get download URL
        Note over Impl: May require<br/>authentication

        Impl->>Provider: HTTP Request (stream)
        activate Provider

        loop Data chunks
            Provider-->>Impl: Binary chunk
            Impl->>FS: Write chunk
        end

        Provider-->>Impl: Download complete
        deactivate Provider

        Impl-->>API: File path
        deactivate Impl

        API-->>Downloader: File path
        deactivate API
    end

    Downloader-->>User: List of paths
    deactivate Downloader
```

---

## Bulk Search Flow (bulk_search)

```mermaid
flowchart TD
    A[Start: bulk_search filters] --> B[First search<br/>search filters]
    B --> C{Results found?}
    C -->|No| D[Return empty results]
    C -->|Yes| E[Save results]
    E --> F[Find oldest<br/>date]
    F --> G[Update end_date<br/>in filters]
    G --> H[New search<br/>search filters]
    H --> I{New<br/>results?}
    I -->|No| J[Return all<br/>results]
    I -->|Yes| K{Filters<br/>changed?}
    K -->|No| J
    K -->|Yes| E

    style A fill:#e1f5ff
    style D fill:#ffcdd2
    style J fill:#c8e6c9
```

**Algorithm Explanation**:

1. **First search**: Executed with original filters
2. **Iteration**: For each set of results:
   - Extract the oldest date
   - Update `end_date` to that date
   - Search again with the reduced range
3. **Termination**: The loop ends when:
   - No more results
   - Filters don't change (same date)

This approach allows handling large date ranges that might exceed API limits.

---

## Package Diagram

```mermaid
graph LR
    subgraph sat_download
        A[api/]
        B[data_types/]
        C[factories/]
        D[services/]
        E[enums.py]
    end

    subgraph api/
        A1[base.py]
        A2[odata.py]
        A3[usgs.py]
    end

    subgraph data_types/
        B1[search.py]
    end

    subgraph factories/
        C1[search.py]
    end

    subgraph services/
        D1[downloader.py]
    end

    A --> A1
    A --> A2
    A --> A3
    B --> B1
    C --> C1
    D --> D1

    D1 --> A1
    A1 --> B1
    A2 --> A1
    A3 --> A1
    A2 --> C1
    A3 --> C1
    C1 --> B1
    C1 --> E
    B1 --> E

    style A fill:#bbdefb
    style B fill:#c5e1a5
    style C fill:#fff9c4
    style D fill:#ffccbc
    style E fill:#f8bbd0
```

## State Diagram: Download Process

```mermaid
stateDiagram-v2
    [*] --> Initialized: __init__(api)

    Initialized --> Searching: search(filters)
    Searching --> ResultsObtained: success
    Searching --> Error: failure

    ResultsObtained --> Downloading: bulk_download()
    Downloading --> DownloadingImage: for each image

    DownloadingImage --> Authenticating
    Authenticating --> RequestingURL
    RequestingURL --> Streaming
    Streaming --> WritingFile
    WritingFile --> ImageDownloaded

    ImageDownloaded --> DownloadingImage: more images
    ImageDownloaded --> Completed: all downloaded

    Error --> [*]
    Completed --> [*]

    note right of Authenticating
        OAuth2 or API Token
    end note

    note right of Streaming
        Download by chunks
        with progress bar
    end note
```

---

## Activity Diagram: Complete Flow

```mermaid
flowchart TD
    Start([User starts program]) --> Init[Create API instance]
    Init --> CreateDownloader[Create SatelliteImageDownloader]
    CreateDownloader --> DefineFilters[Define SearchFilters]

    DefineFilters --> Search{Search type?}
    Search -->|Simple| SearchSimple[search filters]
    Search -->|Bulk| SearchBulk[bulk_search filters]

    SearchSimple --> CheckResults{Results found?}
    SearchBulk --> CheckResults

    CheckResults -->|No| NoResults[Show message]
    CheckResults -->|Yes| ShowResults[Show results]

    ShowResults --> DecideDownload{Download?}
    DecideDownload -->|No| End([End])
    DecideDownload -->|Yes| CreateDir[Create directory]

    CreateDir --> Download[bulk_download]
    Download --> ProcessImages[Process each image]

    ProcessImages --> Authenticate[Authenticate with provider]
    Authenticate --> RequestURL[Request download URL]
    RequestURL --> StreamData[Download data]
    StreamData --> SaveFile[Save file]

    SaveFile --> MoreImages{More images?}
    MoreImages -->|Yes| ProcessImages
    MoreImages -->|No| ShowPaths[Show downloaded paths]

    NoResults --> End
    ShowPaths --> End

    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style Search fill:#fff9c4
    style CheckResults fill:#fff9c4
    style DecideDownload fill:#fff9c4
    style MoreImages fill:#fff9c4
```

---

## Pattern Interaction Diagram

```mermaid
graph TB
    subgraph "User Layer"
        U[User]
    end

    subgraph "Facade Pattern"
        F[SatelliteImageDownloader]
    end

    subgraph "Abstract Factory Pattern"
        AF[SatelliteAPI]
    end

    subgraph "Strategy Pattern"
        S1[ODataAPI Strategy]
        S2[USGSAPI Strategy]
    end

    subgraph "Factory Method Pattern"
        FM[get_satellite_image]
        FM1[get_sentinel2]
        FM2[get_sentinel3]
        FM3[get_landsat_8]
    end

    subgraph "DTO Pattern"
        DTO1[SearchFilters]
        DTO2[SatelliteImage]
        DTO3[SearchResults]
    end

    subgraph "Template Method Pattern"
        TM[bulk_search]
    end

    U --> F
    F --> AF
    AF --> TM
    AF --> S1
    AF --> S2
    S1 --> FM
    S2 --> FM
    FM --> FM1
    FM --> FM2
    FM --> FM3

    F -.uses.-> DTO1
    F -.returns.-> DTO3
    FM -.creates.-> DTO2
    DTO3 -.contains.-> DTO2

    style U fill:#e1f5ff
    style F fill:#b3e5fc
    style AF fill:#81d4fa
    style S1 fill:#4fc3f7
    style S2 fill:#4fc3f7
    style FM fill:#fff9c4
    style DTO1 fill:#c8e6c9
    style DTO2 fill:#c8e6c9
    style DTO3 fill:#c8e6c9
    style TM fill:#ffccbc
```

---

## Summary

These diagrams provide different views of the architecture:

- **Class Diagrams**: Static structure and relationships
- **Component Diagrams**: Modular organization
- **Sequence Diagrams**: Interactions between objects
- **Flow Diagrams**: Process logic
- **State Diagrams**: Object lifecycle
- **Activity Diagrams**: Complete workflows
- **Package Diagrams**: Dependencies between modules

All these diagrams are automatically rendered by MkDocs using Mermaid.js when the documentation is built.
