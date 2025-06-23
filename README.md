# Influencer Data Management System

The Influencer Data Management System (IDMS) is designed to help teams collect, organize, and analyze information about social media influencers. The project aims to centralize influencer profiles, campaign metrics, and related insights in one place.

## Features

- **Influencer Profiles**: Store key attributes like demographics, channel links, and engagement statistics.
- **Campaign Tracking**: Track collaborations, performance metrics, and outreach history.
- **Analytics**: Provide summary statistics and exportable reports.

## Getting Started

This repository currently contains planning documents. Code development will begin soon. The sections below outline the requirements and structure for upcoming contributions.

### Prerequisites

- Python 3.10 or later
- [Poetry](https://python-poetry.org/) for dependency management
- PostgreSQL (for the production database)

### Installing Dependencies

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd Influencer_Data_Management_System
   ```
2. Install the Python dependencies using Poetry:
   ```bash
   poetry install
   ```
   This will create a virtual environment and install all required packages listed in `pyproject.toml`.

### Planned Architecture

- **Backend**: FastAPI for building a RESTful API.
- **Database**: PostgreSQL managed through SQLAlchemy or an ORM of choice.
- **Authentication**: JWT-based authentication for API endpoints.
- **Frontend**: Future integration with a JavaScript framework (React or Vue) for the admin dashboard.

### Directory Layout

The following directory structure is planned for future development:

```
Influencer_Data_Management_System/
├── backend/          # FastAPI application code
│   ├── app/          # Main application package
│   ├── tests/        # API and model tests
│   └── requirements/ # Dependency files
├── data/             # Sample datasets and database migrations
├── docs/             # Project documentation
├── scripts/          # Utility scripts for setup or data import
└── docker/           # Docker configuration files
```

Additional modules may be added as the project evolves. Contributors are encouraged to follow the directory layout and keep documentation up to date.

## Contributing

Contributions are welcome! Please open an issue to discuss new features or bug fixes before submitting a pull request.

## License

This project is licensed under the MIT License.
