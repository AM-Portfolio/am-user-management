# am-user-management
am-user-management/
│
├── core/                          # Minimal shared kernel (domain models, interfaces)
│   ├── value_objects/
│   │   ├── user_id.py             # Immutable UUID wrapper
│   │   ├── email.py               # Validated email
│   │   └── phone_number.py        # E.164 formatted
│   │
│   └── interfaces/
│       ├── repository.py          # ABC: save(), get_by_id()
│       └── event_bus.py           # Abstract: publish(event)
│
├── modules/                       # ✅ Vertical modules — each owns its config, logic, persistence
│   │
│   ├── account_management/        # 🔐 Core identity & authentication
│   │   ├── config/
│   │   │   └── settings.py        # PASSWORD_MIN_LENGTH=8, EMAIL_VERIFICATION_ENABLED=True
│   │   │
│   │   ├── api/
│   │   │   ├── public/
│   │   │   │   ├── auth_router.py           # POST /users, POST /login, POST /reset-password
│   │   │   │   └── schemas.py               # CreateUserRequest, LoginResponse
│   │   │   │
│   │   │   └── internal/
│   │   │       └── user_internal_api.py     # GET /internal/v1/users/{id}
│   │   │
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── create_user.py           # Validates → saves → publishes UserCreated
│   │   │   │   ├── login.py                 # Authenticates → returns session_id (token handled externally)
│   │   │   │   ├── reset_password.py        # Sends reset link via email
│   │   │   │   └── verify_email.py          # Marks user as verified
│   │   │   │
│   │   │   └── services/
│   │   │       ├── password_hasher.py       # Argon2/bcrypt wrapper
│   │   │       └── email_service.py         # Sends verification/reset emails
│   │   │
│   │   ├── domain/
│   │   │   ├── models/
│   │   │   │   └── user_account.py          # Entity: id, email, password_hash, status, verified_at
│   │   │   │
│   │   │   ├── exceptions/
│   │   │   │   ├── user_already_exists.py
│   │   │   │   ├── invalid_credentials.py
│   │   │   │   └── email_not_verified.py
│   │   │   │
│   │   │   └── enums/
│   │   │       └── user_status.py           # ACTIVE, INACTIVE, PENDING_VERIFICATION
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── persistence/
│   │   │   │   ├── sqlalchemy_user_repo.py  # Implements core.interfaces.UserRepository
│   │   │   │   └── user_orm_model.py        # Table: user_accounts
│   │   │   │
│   │   │   └── events/
│   │   │       └── user_created_publisher.py # Publishes UserCreated event
│   │   │
│   │   └── tests/
│   │       ├── unit/
│   │       │   ├── test_create_user.py      # Mocks repo, tests logic
│   │       │   └── test_password_hasher.py
│   │       │
│   │       └── integration/
│   │           └── test_auth_flow.py        # Uses real DB, tests full create → login
│   │
│   ├── user_profile/              # 👤 Personalization & display
│   │   ├── config/
│   │   │   └── settings.py        # MAX_BIO_LENGTH=500, ALLOWED_PICTURE_FORMATS="jpg,png"
│   │   │
│   │   ├── api/
│   │   │   └── public/
│   │   │       ├── profile_router.py        # PATCH /profile, GET /profile
│   │   │       └── schemas.py               # UpdateProfileRequest, ProfileResponse
│   │   │
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       └── update_user_profile.py    # Updates name, bio, picture_url
│   │   │
│   │   ├── domain/
│   │   │   ├── models/
│   │   │   │   └── user_profile.py          # Entity: user_id, first_name, bio, picture_url, timezone
│   │   │   │
│   │   │   └── exceptions/
│   │   │       └── profile_not_found.py
│   │   │
│   │   ├── infrastructure/
│   │   │   └── persistence/
│   │   │       ├── sqlalchemy_profile_repo.py
│   │   │       └── profile_orm_model.py     # Table: user_profiles
│   │   │
│   │   └── tests/
│   │       └── unit/
│   │           └── test_update_profile.py
│   │
│   ├── subscription/              # 💳 Billing & plans
│   │   ├── config/
│   │   │   └── settings.py        # TRIAL_DAYS=14, DEFAULT_CURRENCY="USD", AUTO_RENEW_ENABLED=True
│   │   │
│   │   ├── api/
│   │   │   └── public/
│   │   │       ├── subscription_router.py
│   │   │       └── schemas.py
│   │   │
│   │   ├── application/
│   │   │   └── use_cases/
│   │   │       ├── upgrade_plan.py
│   │   │       ├── cancel_subscription.py
│   │   │       └── start_free_trial.py
│   │   │
│   │   ├── domain/
│   │   │   ├── models/
│   │   │   │   ├── subscription.py          # user_id, plan_id, status, expires_at
│   │   │   │   └── plan.py                  # id, name, price, features
│   │   │   │
│   │   │   └── enums/
│   │   │       └── subscription_status.py    # ACTIVE, CANCELLED, EXPIRED
│   │   │
│   │   ├── infrastructure/
│   │   │   └── persistence/
│   │   │       ├── sqlalchemy_subscription_repo.py
│   │   │       └── subscription_orm_model.py # Tables: subscriptions, plans
│   │   │
│   │   └── tests/
│   │       └── unit/
│   │           └── test_upgrade_plan.py
│   │
│   └── permissions_roles/         # 🔑 RBAC & access control
│       ├── config/
│       │   └── settings.py        # DEFAULT_ROLE="viewer", ROLE_HIERARCHY={"admin": ["editor"]}
│       │
│       ├── api/
│       │   └── public/
│       │       ├── roles_router.py
│       │       └── schemas.py
│       │
│       ├── application/
│       │   └── use_cases/
│       │       ├── assign_role.py
│       │       └── check_permission.py
│       │
│       ├── domain/
│       │   ├── models/
│       │   │   ├── role.py                  # id, name, permissions
│       │   │   └── permission.py            # resource, action (e.g., "user:read")
│       │   │
│       │   └── exceptions/
│       │       └── permission_denied.py
│       │
│       ├── infrastructure/
│       │   └── persistence/
│       │       ├── sqlalchemy_role_repo.py
│       │       └── role_orm_model.py        # Tables: roles, user_roles, permissions
│       │
│       └── tests/
│           └── unit/
│               └── test_check_permission.py
│
├── integration/                   # Cross-module coordination (minimal)
│   ├── events/
│   │   └── handlers/
│   │       ├── start_trial_on_user_created.py  # Listens to UserCreated → triggers subscription.use_cases.start_free_trial
│   │       ├── create_profile_on_user_created.py # Auto-create profile on user creation
│   │       └── notify_token_service_on_user_created.py # Calls am-auth-tokens API to issue initial token
│   │
│   └── contracts/
│       └── v1/
│           ├── user_account_dto.py   # Read-only: id, email, status
│           ├── user_profile_dto.py   # Read-only: first_name, bio, picture_url
│           └── __init__.py           # Exports stable DTOs
│
├── shared_infra/                  # Shared technical concerns
│   ├── config/
│   │   ├── settings.py            # Global config: DATABASE_URL, LOG_LEVEL, ENABLE_EMAIL_SERVICE
│   │   └── feature_flags.py       # Central toggle: ENABLE_ACCOUNT_MANAGEMENT=True
│   │
│   ├── database/
│   │   ├── session.py             # SQLAlchemy session factory
│   │   └── base.py                # DeclarativeBase for ORM
│   │
│   ├── logging/
│   │   └── logger.py              # Structured JSON logger
│   │
│   └── di_container.py            # Dependency injection: wires repos → use cases based on config
│
├── main.py                        # App factory: mounts only enabled module routers
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md                      # "Core user management system. Tokens handled by am-auth-tokens."
