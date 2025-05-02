frontend/
├── public/
│   ├── assets/
│   │   ├── icons/
│   │   └── images/
│   ├── fonts/
│   ├── index.html
│   └── manifest.json
└── src/
    ├── App.js
    ├── index.js
    ├── routes.js
    ├── components/
    │   ├── common/
    │   │   ├── AuthLayout.jsx
    │   │   ├── MainLayout.jsx
    │   │   ├── ProtectedRoute.jsx
    │   │   └── UIComponents/
    │   ├── dashboard/
    │   │   ├── AlertsSummary.jsx
    │   │   ├── GunnySummaryCard.jsx
    │   │   ├── VehicleSummaryCard.jsx
    │   │   └── StatsSummaryGrid.jsx
    │   └── modules/
    │       ├── contextual/
    │       │   ├── VideoResultsList.jsx
    │       │   ├── SearchInterface.jsx
    │       │   └── index.js
    │       ├── facial/
    │       │   ├── FaceCapture/
    │       │   ├── FaceRecognition/
    │       │   ├── FaceRegistration/
    │       │   └── index.js
    │       ├── gunny/
    │       └── vehicle/
    ├── pages/
    │   ├── Dashboard/
    │   ├── ContextualIntelligence/
    │   ├── FacialRecognition/
    │   │   ├── AccessControl.jsx
    │   │   ├── AuthorizationLogs.jsx
    │   │   ├── PersonnelManagement.jsx
    │   │   └── index.jsx
    │   ├── GunnyCounter/
    │   ├── VehicleRecognition/
    │   └── auth/
    │       └── Login.jsx
    ├── services/
    │   └── api/
    │       ├── baseService.js
    │       └── moduleServices/
    │           ├── contextualIntelligenceService.js
    │           ├── facialRecognitionService.js
    │           ├── gunnyCounterService.js
    │           └── vehicleRecognitionService.js
    ├── store/
    │   ├── index.js
    │   └── slices/
    │       ├── authSlice.js
    │       ├── contextSlice.js
    │       ├── facialSlice.js
    │       ├── gunnySlice.js
    │       ├── uiSlice.js
    │       └── vehicleSlice.js
    ├── styles/
    │   └── main.css
    └── utils/
        ├── formatting.js
        ├── validation.js
        └── apiHelpers.js