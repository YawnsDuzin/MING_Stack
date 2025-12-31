/**
 * Node-RED Settings for MING Stack
 * 산업용 IoT 플랫폼 설정
 */

module.exports = {
    // 플로우 파일 설정
    flowFile: 'flows.json',
    flowFilePretty: true,

    // 사용자 디렉토리
    userDir: '/data',

    // 노드 디렉토리
    nodesDir: '/data/nodes',

    // UI 설정
    uiPort: process.env.PORT || 1880,
    uiHost: "0.0.0.0",

    // 에디터 설정
    httpAdminRoot: '/',
    httpNodeRoot: '/api',

    // 보안 설정 (프로덕션에서는 활성화 권장)
    adminAuth: {
        type: "credentials",
        users: [{
            username: "admin",
            password: "$2b$08$wuAqPiKJlVN27eF5qJp.yuYtvYhGLqwGqgF1I3hMlnVNrJz0w5dLS", // admin123
            permissions: "*"
        }, {
            username: "viewer",
            password: "$2b$08$wuAqPiKJlVN27eF5qJp.yuYtvYhGLqwGqgF1I3hMlnVNrJz0w5dLS", // admin123
            permissions: "read"
        }]
    },

    // 크리덴셜 암호화
    credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET || "ming-secret-key",

    // 로깅 설정
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },

    // 에디터 테마
    editorTheme: {
        projects: {
            enabled: false
        },
        header: {
            title: "MING Stack - Node-RED",
            image: null,
        },
        palette: {
            catalogues: [
                'https://catalogue.nodered.org/catalogue.json'
            ]
        },
        tours: false
    },

    // 컨텍스트 저장소 설정
    contextStorage: {
        default: {
            module: "localfilesystem"
        }
    },

    // 함수 노드에서 외부 모듈 사용 허용
    functionExternalModules: true,
    functionGlobalContext: {
        // 글로벌 컨텍스트에 추가할 모듈
    },

    // 디버깅 설정
    debugMaxLength: 1000,

    // MQTT 브로커 기본 설정
    mqttReconnectTime: 15000,

    // 직렬화 설정
    serialWarning: true,

    // HTTP 요청 타임아웃
    httpRequestTimeout: 120000,

    // 런타임 API 비활성화 (보안)
    disableEditor: false,
    httpNodeCors: {
        origin: "*",
        methods: "GET,PUT,POST,DELETE"
    }
};
