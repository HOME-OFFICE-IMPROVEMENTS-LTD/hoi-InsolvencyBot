# Changelog

All notable changes to InsolvencyBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern UI design with comprehensive CSS design system
  - Design tokens for colors, typography, spacing, and shadows
  - Responsive components including cards, buttons, and form elements
  - Modern utility classes for flexible layouts
- Enhanced web interface with responsive design across devices
  - Improved navigation with header and footer components
  - Example questions section for better user guidance
  - Visual API status indicators with pulse animation
  - User feedback mechanism (thumbs up/down) for responses
- New status monitoring page with real-time resource visualization
  - Visual system health indicators with color-coded status
  - Resource usage progress bars for CPU, memory, and disk
  - Auto-refresh with visual countdown and progress bar
  - Loading indicators and improved visualization
- New API endpoint to collect user feedback
  - Backend storage of feedback for response quality tracking
  - API endpoint documentation added
  - Auto-refresh functionality with countdown timer
  - Collapsible detailed information sections
- API health and diagnostic endpoints for system monitoring
  - New `/api/feedback` endpoint for collecting user feedback
  - Enhanced diagnostic information with uptime tracking
- Improved load testing with detailed performance reports
- Advanced error handling and user feedback mechanisms
  - Thumbs up/down feedback mechanism for responses
  - Improved error display with visual indicators
- REST API using FastAPI with Swagger documentation
- API client in Python for programmatic access
- Docker and docker-compose configuration for containerized deployment
- Flask web demo application with modern and classic UI options
- Comprehensive API documentation with examples
- Production deployment scripts and guides
- Architecture diagrams and technical documentation
- Advanced usage examples for integration
- API tests with automated test suite
- Code coverage measurement and reporting
- Sphinx documentation generator
- Enhanced security features with API key authentication
- Detailed security considerations in documentation
- Additional architecture diagrams (sequence and deployment)
- Improved load testing capabilities
- Extended API client with better error handling
- GitHub Actions workflow for automated testing
- Extract references feature to identify legislation, cases, and forms
- Proper error handling and retries for API calls
- Authentication for API endpoints with API key support
- CONTRIBUTING.md guide for new contributors
- This CHANGELOG file
- Metrics collection for API usage, response times, and error rates
- Connection health check for API/web communication
- Rate limiting middleware to prevent abuse
- Centralized configuration management
- Full integration between web UI and API service
- Diagnostic endpoint for system health monitoring
- System status page with real-time metrics
- Combined run_system.sh script for full system deployment
- API connectivity testing features
- Auto-refreshing monitoring capabilities

### Changed
- Enhanced Makefile with additional targets
- Updated requirements.txt with additional dependencies
- Improved docstrings and API documentation
- Refactored answer_question function with better error handling
- Separated web interface to use API backend instead of direct LLM calls
- Enhanced error handling for API connectivity issues
- Improved API key validation with clear error messages

### Fixed
- Import path issues in __main__.py
- Integration tests stability
- Indentation issues in API endpoint implementations
- API error reporting consistency
- Web UI error handling for API connection failures

## [1.1.0] - 2023-06-15

### Added
- System monitoring and status features:
  - API diagnostic endpoint with comprehensive system metrics
  - Interactive web interface status page with real-time monitoring
  - Visual resource utilization indicators (CPU, memory, disk)
  - Auto-refreshing status dashboard with usage statistics
  - API connectivity status indicators
  - System health check script (check_status.sh)
  - Unified system run script (run_system.sh)
- Enhanced load testing capabilities:
  - Advanced load testing script with detailed metrics
  - HTML report generation with visualizations
  - Progressive load testing with ramp-up capability
  - Response time distribution analysis
  - Test request history and error tracking

### Changed
- Updated API implementation with improved error handling
- Enhanced web interface to use API backend instead of direct LLM calls
- Unified API and web interface with better integration
- Improved documentation with status and monitoring information
- Updated requirements.txt with new dependencies
- Added comprehensive exception handling for better diagnostics

### Fixed
- Fixed import errors in API implementation
- Resolved indentation issues in process_question function
- Fixed API connectivity issues in web interface
- Improved error handling with the RequestTracker class
- Enhanced status page template for better readability and visualization

## [0.1.0] - 2023-04-15

### Added
- Initial release with basic functionality
- Implementation of answer_question function
- Rudimentary test suite
- Support for multiple OpenAI models (gpt-3.5-turbo, gpt-4, gpt-4o)

[Unreleased]: https://github.com/HOME-OFFICE-IMPROVEMENTS-LTD/hoi-InsolvencyBot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/HOME-OFFICE-IMPROVEMENTS-LTD/hoi-InsolvencyBot/releases/tag/v0.1.0
[1.1.0]: https://github.com/HOME-OFFICE-IMPROVEMENTS-LTD/hoi-InsolvencyBot/releases/tag/v1.1.0
