"""100k+ yuksek kaliteli egitim verisi uretici — v2.

v1'deki sabit yapi sorununu cozer: her ornek farkli bir
cikti yapisina, farkli zenginliklere sahip olur.

12+ archetype (yapi sablonu) x 9 hedef profil x 10 dil x
degisken zenginlikler (soru, sistem promptu, bellek, varsayim...)
ile benzersiz, cesitli (input, output) ciftleri uretir.

Kullanim:
    python -m training.data.generate_v2 --count 100000
    python -m training.data.generate_v2 --count 5000 --lang tr --target claude-code
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from reprompt.prompts.types import TARGET_PROFILES

console = Console()

OUT_PATH = Path("training/datasets/raw/synthetic_v2.jsonl")

LANGS = ["tr", "en", "de", "fr", "es", "pt", "ru", "ja", "zh", "ko"]
TARGETS = list(TARGET_PROFILES)

# Konular — kategori bazinda organize

TOPIC_POOLS = {
    "frontend": {
        "tr": [
            "login sayfasi",
            "kayit formu",
            "profil sayfasi",
            "dashboard",
            "dark mode",
            "responsive tasarim",
            "form validasyonu",
            "modal dialog",
            "tablo componenti",
            "drag and drop",
            "infinite scroll",
            "toast bildirimi",
            "autocomplete",
            "skeleton loader",
            "progress bar",
            "animasyon",
            "sidebar menu",
            "breadcrumb",
            "tab navigasyonu",
            "dosya yukleyici",
            "tarih secici",
            "renk paleti",
            "avatar yukleme",
            "yorum kutusu",
        ],
        "en": [
            "login page",
            "registration form",
            "profile page",
            "dashboard layout",
            "dark mode toggle",
            "responsive design",
            "form validation",
            "modal dialog",
            "data table",
            "drag and drop",
            "infinite scroll",
            "toast notification",
            "autocomplete input",
            "skeleton loader",
            "progress indicator",
            "CSS animation",
            "sidebar navigation",
            "breadcrumb",
            "tab component",
            "file uploader",
            "date picker",
            "color picker",
            "avatar upload",
            "comment box",
        ],
        "de": [
            "Anmeldeseite",
            "Registrierungsformular",
            "Profilseite",
            "Dashboard",
            "Dunkelmodus",
            "Responsive Design",
            "Formularvalidierung",
            "Modaler Dialog",
            "Datentabelle",
            "Drag and Drop",
            "Endlos-Scrollen",
            "Toast-Benachrichtigung",
            "Autovervollstaendigung",
            "Skeleton-Loader",
            "Fortschrittsanzeige",
            "Animation",
        ],
        "fr": [
            "page de connexion",
            "formulaire d'inscription",
            "page de profil",
            "tableau de bord",
            "mode sombre",
            "design responsive",
            "validation de formulaire",
            "boite modale",
            "table de donnees",
            "glisser-deposer",
            "defilement infini",
            "notification toast",
            "autocompletion",
            "indicateur de progression",
            "selecteur de date",
            "navigation laterale",
        ],
        "es": [
            "pagina de login",
            "formulario de registro",
            "pagina de perfil",
            "tablero",
            "modo oscuro",
            "diseno responsivo",
            "validacion de formulario",
            "dialogo modal",
            "tabla de datos",
            "arrastrar y soltar",
            "scroll infinito",
            "notificacion emergente",
            "autocompletado",
            "indicador de progreso",
            "selector de fecha",
            "navegacion lateral",
        ],
        "pt": [
            "pagina de login",
            "formulario de cadastro",
            "pagina de perfil",
            "painel",
            "modo escuro",
            "design responsivo",
            "validacao de formulario",
            "dialogo modal",
            "tabela de dados",
            "arrastar e soltar",
            "rolagem infinita",
            "notificacao toast",
            "autocompletar",
            "indicador de progresso",
            "seletor de data",
            "navegacao lateral",
        ],
        "ru": [
            "stranica vhoda",
            "forma registracii",
            "stranica profilja",
            "panel upravlenija",
            "temnaja tema",
            "adaptivnyj dizajn",
            "validacija formy",
            "modalnoe okno",
            "tablica dannyh",
            "peretaskivanie",
            "beskonechnaja prokrutka",
            "vsplyvajuschee uvedomlenie",
        ],
        "ja": [
            "roguin peeji",
            "touroku foomu",
            "purofiru peeji",
            "dasshubodo",
            "daaku moodo",
            "resuponsibu dezain",
            "foomu barideshon",
            "moodaru daiaorogu",
            "deeta teeburu",
            "doragu ando doroppu",
            "mugen sukurooru",
            "toosuto tsuuchi",
        ],
        "zh": [
            "denglu yemian",
            "zhuce biaoduan",
            "geren ziliao ye",
            "yibiao pan",
            "an se moshi",
            "xiangying shi sheji",
            "biaodan yanzheng",
            "motai kuang",
            "shuju biao",
            "tuozhuai",
            "wuxian gundong",
            "tanchu tongzhi",
        ],
        "ko": [
            "roguin peiji",
            "deungnok pom",
            "peuropil peiji",
            "daesibodeu",
            "dakeu modeu",
            "baneunghyeong dijain",
            "pom yuhyoseong geomsa",
            "modal daiallogeu",
            "deiteo teibul",
            "deuraegeu aen deulop",
            "muhanjeongseo seukeulol",
            "toseuteu alrim",
        ],
    },
    "backend": {
        "tr": [
            "REST endpoint",
            "GraphQL schema",
            "websocket baglantisi",
            "kuyruk sistemi",
            "cache katmani",
            "rate limiter",
            "health check",
            "logging sistemi",
            "cron job",
            "webhook handler",
            "dosya depolama",
            "e-posta gonderici",
            "veritabani migration",
            "seed data",
            "ORM modeli",
            "middleware",
            "background worker",
            "event bus",
            "API gateway",
            "servis kesfedici",
        ],
        "en": [
            "REST API endpoint",
            "GraphQL resolver",
            "websocket connection",
            "message queue",
            "cache layer",
            "rate limiter",
            "health check endpoint",
            "structured logging",
            "cron scheduler",
            "webhook handler",
            "file storage service",
            "email sender",
            "database migration",
            "seed data script",
            "ORM model",
            "middleware",
            "background worker",
            "event bus",
            "API gateway",
            "service discovery",
        ],
        "de": [
            "REST-API-Endpunkt",
            "GraphQL-Resolver",
            "WebSocket-Verbindung",
            "Nachrichtenwarteschlange",
            "Cache-Schicht",
            "Ratenbegrenzung",
            "Gesundheitscheck",
            "Protokollierung",
            "Cron-Scheduler",
            "Webhook-Handler",
            "Dateispeicher",
            "E-Mail-Versand",
            "Datenbankumstellung",
            "ORM-Modell",
            "Middleware",
            "Hintergrundarbeiter",
        ],
        "fr": [
            "endpoint REST",
            "resolveur GraphQL",
            "connexion WebSocket",
            "file de messages",
            "couche de cache",
            "limiteur de debit",
            "verification de sante",
            "journalisation",
            "planificateur cron",
            "gestionnaire de webhook",
            "stockage de fichiers",
            "envoi d'email",
            "migration de base de donnees",
            "modele ORM",
            "middleware",
            "worker en arriere-plan",
        ],
        "es": [
            "endpoint REST",
            "resolvedor GraphQL",
            "conexion WebSocket",
            "cola de mensajes",
            "capa de cache",
            "limitador de velocidad",
            "verificacion de estado",
            "registro estructurado",
            "planificador cron",
            "manejador de webhook",
            "almacenamiento de archivos",
            "envio de email",
            "migracion de base de datos",
            "modelo ORM",
            "middleware",
            "worker en segundo plano",
        ],
        "pt": [
            "endpoint REST",
            "resolver GraphQL",
            "conexao WebSocket",
            "fila de mensagens",
            "camada de cache",
            "limitador de taxa",
            "verificacao de saude",
            "registro estruturado",
            "agendador cron",
            "manipulador de webhook",
            "armazenamento de arquivos",
            "envio de email",
            "migracao de banco de dados",
            "modelo ORM",
            "middleware",
            "worker em segundo plano",
        ],
        "ru": [
            "REST endpoynt",
            "GraphQL rezolver",
            "WebSocket-soedinenie",
            "ochered soobschenij",
            "sloj keshirovanija",
            "ogranichitel skorosti",
            "proverka zdorovja",
            "strukturirovannoe zhurnalirovanie",
            "cron planirovschik",
            "obrabotchik webhookov",
            "fajlovoe hranilische",
            "otpravka email",
        ],
        "ja": [
            "REST endopointo",
            "GraphQL rizorubaa",
            "WebSocket setsuzoku",
            "messeeji kyuu",
            "kyasshu reiyaa",
            "reeto rimitaa",
            "herusu chekku",
            "rogingu shisutemu",
            "kuron sukejuuraa",
            "webhook handoraa",
            "fairu sutoreji",
            "meeru soushin",
        ],
        "zh": [
            "REST duankou",
            "GraphQL jiexi qi",
            "WebSocket lianjie",
            "xiaoxi duilie",
            "huancun ceng",
            "sudu xianzhi qi",
            "jiankang jiancha",
            "jiegohua rizhi",
            "dingshi renwu",
            "webhook chuliqì",
            "wenjian cunchu",
            "youjian fasong",
        ],
        "ko": [
            "REST endeupoindeu",
            "GraphQL rijeolbeo",
            "WebSocket yeongyeol",
            "mesiji kyu",
            "kaesi gyecheung",
            "soddo jeghan gi",
            "sangtae hwanin",
            "gujojeok roging",
            "keuron seukejulleo",
            "webhook haendeuleo",
            "pail jeojangso",
            "imeil balsong",
        ],
    },
    "devops": {
        "tr": [
            "CI/CD pipeline",
            "Docker container",
            "nginx reverse proxy",
            "Kubernetes deployment",
            "monitoring dashboard",
            "alert sistemi",
            "log aggregation",
            "secret management",
            "load balancer",
            "auto-scaling",
            "backup stratejisi",
            "rollback mekanizmasi",
        ],
        "en": [
            "CI/CD pipeline",
            "Docker containerization",
            "nginx reverse proxy",
            "Kubernetes deployment",
            "monitoring setup",
            "alerting system",
            "log aggregation",
            "secrets management",
            "load balancer config",
            "auto-scaling policy",
            "backup strategy",
            "rollback mechanism",
        ],
        "de": [
            "CI/CD-Pipeline",
            "Docker-Containerisierung",
            "Nginx-Reverse-Proxy",
            "Kubernetes-Bereitstellung",
            "Monitoring-Einrichtung",
            "Alarmsystem",
            "Log-Aggregation",
            "Geheimnisverwaltung",
        ],
        "fr": [
            "pipeline CI/CD",
            "conteneurisation Docker",
            "proxy inverse Nginx",
            "deploiement Kubernetes",
            "configuration monitoring",
            "systeme d'alerte",
            "aggregation de logs",
            "gestion des secrets",
        ],
        "es": [
            "pipeline CI/CD",
            "contenerizacion Docker",
            "proxy inverso Nginx",
            "despliegue Kubernetes",
            "configuracion de monitoreo",
            "sistema de alertas",
            "agregacion de logs",
            "gestion de secretos",
        ],
        "pt": [
            "pipeline CI/CD",
            "contenerizacao Docker",
            "proxy reverso Nginx",
            "deploy Kubernetes",
            "configuracao de monitoramento",
            "sistema de alertas",
            "agregacao de logs",
            "gestao de segredos",
        ],
        "ru": [
            "CI/CD konvejer",
            "Docker kontejnerizacija",
            "Nginx obratnyj proksi",
            "Kubernetes razvertyvanie",
            "nastrojka monitoringa",
            "sistema opoveschenij",
            "agregacija logov",
            "upravlenie sekretami",
        ],
        "ja": [
            "CI/CD paipurain",
            "Docker kontena",
            "Nginx ribaasu purokishi",
            "Kubernetes deburoi",
            "monitaringu",
            "araato shisutemu",
            "rogu shuuyaku",
            "shiikuretto kanri",
        ],
        "zh": [
            "CI/CD liushuixian",
            "Docker rongqi hua",
            "Nginx fan xiang daili",
            "Kubernetes bushu",
            "jiankong peizhi",
            "gaojing xitong",
            "rizhi juhe",
            "miyao guanli",
        ],
        "ko": [
            "CI/CD paipeurain",
            "Docker keonteineo hwa",
            "Nginx yeog-banghyang peuloksi",
            "Kubernetes baepho",
            "moniteoling seoljeong",
            "alrim siseutem",
            "logeu jipgye",
            "bimilbeon gwanli",
        ],
    },
    "security": {
        "tr": [
            "OAuth entegrasyonu",
            "JWT token yonetimi",
            "RBAC yetkilendirme",
            "CSRF korumasi",
            "XSS onleme",
            "SQL injection korumasi",
            "rate limiting",
            "guvenlik audit",
            "sifre politikasi",
            "iki faktorlu dogrulama",
            "IP engelleme",
            "SSL sertifikasi",
        ],
        "en": [
            "OAuth integration",
            "JWT token management",
            "RBAC authorization",
            "CSRF protection",
            "XSS prevention",
            "SQL injection guard",
            "rate limiting",
            "security audit",
            "password policy",
            "two-factor auth",
            "IP blocking",
            "SSL certificate setup",
        ],
        "de": [
            "OAuth-Integration",
            "JWT-Token-Verwaltung",
            "RBAC-Autorisierung",
            "CSRF-Schutz",
            "XSS-Praevention",
            "SQL-Injection-Schutz",
            "Sicherheitsaudit",
            "Passwortrichtlinie",
        ],
        "fr": [
            "integration OAuth",
            "gestion des jetons JWT",
            "autorisation RBAC",
            "protection CSRF",
            "prevention XSS",
            "protection injection SQL",
            "audit de securite",
            "politique de mot de passe",
        ],
        "es": [
            "integracion OAuth",
            "gestion de tokens JWT",
            "autorizacion RBAC",
            "proteccion CSRF",
            "prevencion XSS",
            "proteccion contra inyeccion SQL",
            "auditoria de seguridad",
            "politica de contrasenas",
        ],
        "pt": [
            "integracao OAuth",
            "gestao de tokens JWT",
            "autorizacao RBAC",
            "protecao CSRF",
            "prevencao XSS",
            "protecao contra SQL injection",
            "auditoria de seguranca",
            "politica de senhas",
        ],
        "ru": [
            "OAuth integracija",
            "upravlenie JWT tokenami",
            "RBAC avtorizacija",
            "zaschita ot CSRF",
            "predotvrashchenie XSS",
            "zaschita ot SQL injekcij",
            "audit bezopasnosti",
            "politika parolej",
        ],
        "ja": [
            "OAuth tougou",
            "JWT tookun kanri",
            "RBAC kengen kanri",
            "CSRF bougyo",
            "XSS boushi",
            "SQL injekushon taisaku",
            "sekyuriti kansa",
            "pasuwado porishi",
        ],
        "zh": [
            "OAuth jicheng",
            "JWT lingpai guanli",
            "RBAC shouquan",
            "CSRF fanghu",
            "XSS fangfan",
            "SQL zhuru fanghu",
            "anquan shenji",
            "mima celue",
        ],
        "ko": [
            "OAuth tonghap",
            "JWT tokun gwanli",
            "RBAC gwonhan",
            "CSRF bangeo",
            "XSS bangjji",
            "SQL injeksyeon bangeo",
            "boan gamsa",
            "bimilbeonho jeongchaek",
        ],
    },
    "testing": {
        "tr": [
            "unit test",
            "integration test",
            "e2e test",
            "test altyapisi",
            "mock/stub olusturma",
            "test coverage",
            "snapshot test",
            "load test",
            "regression test",
            "A/B test",
            "mutation test",
            "property-based test",
        ],
        "en": [
            "unit tests",
            "integration tests",
            "end-to-end tests",
            "test infrastructure",
            "mock/stub setup",
            "test coverage report",
            "snapshot testing",
            "load testing",
            "regression tests",
            "A/B testing framework",
            "mutation testing",
            "property-based testing",
        ],
        "de": [
            "Unit-Tests",
            "Integrationstests",
            "End-to-End-Tests",
            "Testinfrastruktur",
            "Mock/Stub-Erstellung",
            "Testabdeckung",
            "Snapshot-Tests",
            "Lasttests",
        ],
        "fr": [
            "tests unitaires",
            "tests d'integration",
            "tests end-to-end",
            "infrastructure de test",
            "creation de mocks",
            "couverture de test",
            "tests snapshot",
            "tests de charge",
        ],
        "es": [
            "pruebas unitarias",
            "pruebas de integracion",
            "pruebas end-to-end",
            "infraestructura de pruebas",
            "creacion de mocks",
            "cobertura de pruebas",
            "pruebas de snapshot",
            "pruebas de carga",
        ],
        "pt": [
            "testes unitarios",
            "testes de integracao",
            "testes end-to-end",
            "infraestrutura de testes",
            "criacao de mocks",
            "cobertura de testes",
            "testes de snapshot",
            "testes de carga",
        ],
        "ru": [
            "modul'nye testy",
            "integracionnye testy",
            "e2e testy",
            "testovaja infrastruktura",
            "sozdanie mokov",
            "pokrytie testami",
            "snapshot testy",
            "nagruzochnye testy",
        ],
        "ja": [
            "yunitto tesuto",
            "tougou tesuto",
            "e2e tesuto",
            "tesuto infura",
            "mokku sakusei",
            "tesuto kabarejji",
            "sunappushotto tesuto",
            "fuka tesuto",
        ],
        "zh": [
            "danwei ceshi",
            "jicheng ceshi",
            "duanduan ceshi",
            "ceshi jichu sheshi",
            "mock chuangjian",
            "ceshi fugailv",
            "kuaizhao ceshi",
            "yali ceshi",
        ],
        "ko": [
            "yunit teseuteu",
            "tonghap teseuteu",
            "e2e teseuteu",
            "teseuteu infra",
            "mog saengseong",
            "teseuteu keobeolijji",
            "seunaepsat teseuteu",
            "buhwa teseuteu",
        ],
    },
    "writing": {
        "tr": [
            "blog yazisi",
            "teknik dokumantasyon",
            "API referansi",
            "hata raporu",
            "toplanti ozeti",
            "proje ozeti",
            "release notu",
            "performans raporu",
            "guvenlik degerlendirmesi",
            "sunum",
            "e-posta taslagi",
            "urun aciklamasi",
            "test plani",
            "mimari karar belgesi",
            "kullanici kilavuzu",
            "changelog",
        ],
        "en": [
            "blog post",
            "technical documentation",
            "API reference",
            "bug report",
            "meeting summary",
            "project brief",
            "release notes",
            "performance report",
            "security assessment",
            "presentation",
            "email draft",
            "product description",
            "test plan",
            "architecture decision record",
            "user guide",
            "changelog",
        ],
        "de": [
            "Blogbeitrag",
            "Technische Dokumentation",
            "API-Referenz",
            "Fehlerbericht",
            "Besprechungsprotokoll",
            "Projektbeschreibung",
            "Release-Notizen",
            "Leistungsbericht",
            "Sicherheitsbewertung",
            "Praesentation",
            "E-Mail-Entwurf",
            "Produktbeschreibung",
        ],
        "fr": [
            "article de blog",
            "documentation technique",
            "reference API",
            "rapport de bug",
            "resume de reunion",
            "brief de projet",
            "notes de version",
            "rapport de performance",
            "evaluation de securite",
            "presentation",
            "brouillon d'email",
            "description de produit",
        ],
        "es": [
            "articulo de blog",
            "documentacion tecnica",
            "referencia API",
            "informe de errores",
            "resumen de reunion",
            "brief de proyecto",
            "notas de version",
            "informe de rendimiento",
            "evaluacion de seguridad",
            "presentacion",
            "borrador de email",
            "descripcion de producto",
        ],
        "pt": [
            "artigo de blog",
            "documentacao tecnica",
            "referencia de API",
            "relatorio de bug",
            "resumo de reuniao",
            "resumo do projeto",
            "notas de versao",
            "relatorio de desempenho",
            "avaliacao de seguranca",
            "apresentacao",
            "rascunho de email",
            "descricao do produto",
        ],
        "ru": [
            "statja v blog",
            "tehnicheskaja dokumentacija",
            "spravka po API",
            "otchet ob oshibke",
            "protokol soveschanija",
            "kratkoe opisanie proekta",
            "zametki o relize",
            "otchet o proizvoditelnosti",
        ],
        "ja": [
            "burogu kiji",
            "gijutsu dokyumento",
            "API refarensu",
            "bagu repooto",
            "kaigi giyouroku",
            "purojekuto gaiyou",
            "ririisu nooto",
            "pafoomansu repooto",
        ],
        "zh": [
            "bowen",
            "jishu wendang",
            "API cankaoshu",
            "cuowu baogao",
            "huiyi zongjie",
            "xiangmu jieshao",
            "banben shuoming",
            "xingneng baogao",
        ],
        "ko": [
            "beullogeu geul",
            "gisul munseo",
            "API chamjo",
            "beogeu bogoseo",
            "hoeui yoyak",
            "peurojekteu gaeyo",
            "riliseu noteu",
            "seongnong bogoseo",
        ],
    },
}

# Ham prompt sablonlari — konusma tarzi cesitleri

RAW_STYLES = {
    "terse": {
        "tr": [
            "{topic} yap",
            "{topic} ekle",
            "{topic} duzelt",
            "{topic} olustur",
            "bi {topic} lazim",
            "{topic} kaldir",
            "{topic} calistir",
        ],
        "en": [
            "make {topic}",
            "add {topic}",
            "fix {topic}",
            "create {topic}",
            "need {topic}",
            "remove {topic}",
            "setup {topic}",
        ],
        "de": [
            "{topic} erstellen",
            "{topic} reparieren",
            "{topic} hinzufuegen",
            "brauche {topic}",
            "{topic} entfernen",
        ],
        "fr": [
            "creer {topic}",
            "corriger {topic}",
            "ajouter {topic}",
            "besoin de {topic}",
            "supprimer {topic}",
        ],
        "es": [
            "crear {topic}",
            "arreglar {topic}",
            "agregar {topic}",
            "necesito {topic}",
            "eliminar {topic}",
        ],
        "pt": [
            "criar {topic}",
            "corrigir {topic}",
            "adicionar {topic}",
            "preciso de {topic}",
            "remover {topic}",
        ],
        "ru": [
            "sdelaj {topic}",
            "pochini {topic}",
            "dobav {topic}",
            "nuzhen {topic}",
            "uberi {topic}",
        ],
        "ja": [
            "{topic} tsukutte",
            "{topic} naoshite",
            "{topic} tsuika shite",
            "{topic} hitsuyou",
            "{topic} keshite",
        ],
        "zh": [
            "zuo {topic}",
            "xiufu {topic}",
            "tianjia {topic}",
            "xuyao {topic}",
            "shanchu {topic}",
        ],
        "ko": [
            "{topic} mandeulgi",
            "{topic} gochigi",
            "{topic} chuga",
            "{topic} pilyohabnida",
            "{topic} sakje",
        ],
    },
    "frustrated": {
        "tr": [
            "{topic} calismiyor duzelt",
            "{topic} patladi",
            "su {topic} bozuk",
            "{topic} kodu cok cirkin",
            "{topic} hata veriyor bak",
            "{topic} yine bozuldu ya",
            "gene {topic} patlamis",
            "{topic} ne bicim bu",
        ],
        "en": [
            "{topic} is broken fix it",
            "{topic} crashed again",
            "the {topic} is buggy",
            "{topic} code is a mess",
            "{topic} keeps throwing errors",
            "{topic} broke again ffs",
            "why is {topic} so slow",
            "{topic} sucks fix it",
        ],
        "de": [
            "{topic} funktioniert nicht mehr",
            "{topic} ist abgestuerzt",
            "{topic} ist fehlerhaft",
            "{topic} Code ist chaotisch",
            "{topic} wirft staendig Fehler",
        ],
        "fr": [
            "{topic} ne fonctionne plus",
            "{topic} a plante",
            "{topic} est buggue",
            "le code de {topic} est un desastre",
            "{topic} lance des erreurs tout le temps",
        ],
        "es": [
            "{topic} no funciona",
            "{topic} se cayo otra vez",
            "{topic} tiene errores",
            "el codigo de {topic} es un desastre",
            "{topic} lanza errores constantemente",
        ],
        "pt": [
            "{topic} parou de funcionar",
            "{topic} travou de novo",
            "{topic} esta com bug",
            "o codigo do {topic} ta horrivel",
            "{topic} da erro toda hora",
        ],
        "ru": [
            "{topic} ne rabotaet pochini",
            "{topic} opyat slomalsja",
            "{topic} gljuchit",
            "kod {topic} uzhasen",
            "{topic} postojanno vydaet oshibki",
        ],
        "ja": [
            "{topic} ugokimasen naoshite",
            "{topic} kurasshu shita",
            "{topic} bagu darake",
            "{topic} koodo kitanai",
            "{topic} eraa bakari deru",
        ],
        "zh": [
            "{topic} huaile xiufu yixia",
            "{topic} bengkui le",
            "{topic} you bug",
            "{topic} daima hen luan",
            "{topic} yizhi baocuo",
        ],
        "ko": [
            "{topic} i jakdonghaji anseumnida",
            "{topic} i chungdol haesseumnida",
            "{topic} e beogeu isseoyo",
            "{topic} kodeu eojileowoyo",
            "{topic} gyesok eleo naseubnida",
        ],
    },
    "descriptive": {
        "tr": [
            "{topic} icin bir cozum lazim, mevcut yapi yetersiz kaliyor",
            "{topic} ozelligini eklememiz gerekiyor, kullanicilar talep etti",
            "{topic} performansi dusuk, iyilestirmemiz sart",
            "yeni bir {topic} modulu gerekiyor, mevcut olan ihtiyaci karsilamiyor",
            "{topic} konusunda refactoring yapmamiz lazim, teknik borc birikiyor",
        ],
        "en": [
            "we need a solution for {topic}, current approach isn't scaling",
            "need to add {topic} feature, users have been requesting it",
            "{topic} performance is degrading, needs optimization",
            "we need a new {topic} module, the existing one doesn't meet requirements",
            "{topic} needs refactoring, tech debt is piling up",
        ],
        "de": [
            "wir brauchen eine Loesung fuer {topic}, der aktuelle Ansatz skaliert nicht",
            "{topic}-Funktion muss hinzugefuegt werden, Benutzer haben es angefordert",
            "{topic}-Leistung verschlechtert sich, braucht Optimierung",
        ],
        "fr": [
            "nous avons besoin d'une solution pour {topic}, l'approche actuelle ne scale pas",
            "il faut ajouter la fonctionnalite {topic}, les utilisateurs la demandent",
            "les performances de {topic} se degradent, optimisation necessaire",
        ],
        "es": [
            "necesitamos una solucion para {topic}, el enfoque actual no escala",
            "hay que agregar la funcionalidad de {topic}, los usuarios la piden",
            "el rendimiento de {topic} se degrada, necesita optimizacion",
        ],
        "pt": [
            "precisamos de uma solucao para {topic}, a abordagem atual nao escala",
            "precisa adicionar a funcionalidade de {topic}, usuarios estao pedindo",
            "o desempenho de {topic} esta caindo, precisa de otimizacao",
        ],
        "ru": [
            "nam nuzhno reshenie dlja {topic}, tekuschij podhod ne masshtabiruetsja",
            "nado dobavit funkcional {topic}, polzovateli prosili",
            "proizvoditelnost {topic} padaet, nuzhna optimizacija",
        ],
        "ja": [
            "{topic} no kaiketsu saku ga hitsuyou, genzai no houhou dewa tarinai",
            "{topic} kinoo wo tsuika suru hitsuyou ga aru, yuuzaa kara no youbou",
            "{topic} no pafoomansu ga teika, saitekika ga hitsuyou",
        ],
        "zh": [
            "women xuyao {topic} de jiejue fangan, muqian de fangfa wufa kuozhan",
            "xuyao tianjia {topic} gongneng, yonghu yizhi zai yaoqiu",
            "{topic} xingneng xiajiang, xuyao youhua",
        ],
        "ko": [
            "{topic} e daehan haegyeol chaegi pilyohabnida, hyeonjae jeobgeun bangsigeun hwakjang bulga",
            "{topic} gineungeul chugahaeya habnida, sayongja yogu sahangibnida",
            "{topic} seongneongi jeoha doegoisseoyo, choejeoghwa pilyohabnida",
        ],
    },
    "vague": {
        "tr": [
            "su {topic} mevzusuna bi bak",
            "{topic} ile ilgili bisey yap",
            "{topic} var ya onu hallet",
            "{topic} konusu",
            "{topic} isine bi el at",
            "ya su {topic} meselesin de bi baksan",
            "{topic} ile ugras biraz",
        ],
        "en": [
            "look into {topic}",
            "do something about {topic}",
            "handle the {topic} thing",
            "can you check {topic}",
            "work on {topic} a bit",
            "something's off with {topic}",
            "{topic} needs attention",
            "take a look at {topic}",
        ],
        "de": [
            "schau dir {topic} an",
            "mach was mit {topic}",
            "kuemmere dich um {topic}",
            "check mal {topic}",
        ],
        "fr": [
            "regarde {topic}",
            "fais quelque chose avec {topic}",
            "occupe-toi de {topic}",
            "verifie {topic}",
        ],
        "es": ["revisa {topic}", "haz algo con {topic}", "encargete de {topic}", "checa {topic}"],
        "pt": [
            "da uma olhada no {topic}",
            "faz alguma coisa com {topic}",
            "cuida do {topic}",
            "verifica {topic}",
        ],
        "ru": [
            "posmotri {topic}",
            "sdelaj chto-nibud s {topic}",
            "zajmis {topic}",
            "prover {topic}",
        ],
        "ja": ["{topic} mite", "{topic} nanika yatte", "{topic} tanomu", "{topic} chekku shite"],
        "zh": [
            "kan yixia {topic}",
            "chuli yixia {topic}",
            "guanli yixia {topic}",
            "jiancha {topic}",
        ],
        "ko": [
            "{topic} jom bwajuseyo",
            "{topic} eotteokhae bwajuseyo",
            "{topic} cheolihaejuseyo",
            "{topic} hwaninhae juseyo",
        ],
    },
    "contextual": {
        "tr": [
            "dun konustugumuz {topic} konusuna devam edelim",
            "gecen hafta basladigimiz {topic} islemi var, onu bitirmemiz lazim",
            "onceki PR'daki {topic} degisikligini guncellememiz gerekiyor",
            "sprint planimizda {topic} vardi, ona bakalim",
            "musteriden {topic} hakkinda sikayet geldi, acil bakmamiz lazim",
        ],
        "en": [
            "let's continue with the {topic} we discussed yesterday",
            "there's the {topic} work from last sprint, need to finish it",
            "need to update the {topic} changes from the previous PR",
            "{topic} was in our sprint plan, let's work on it",
            "got a customer complaint about {topic}, need to look at it urgently",
        ],
        "de": [
            "lass uns mit {topic} weitermachen, das wir gestern besprochen haben",
            "die {topic}-Arbeit vom letzten Sprint muss fertig werden",
            "{topic} war in unserem Sprint-Plan, lass uns daran arbeiten",
        ],
        "fr": [
            "continuons avec {topic} dont on a parle hier",
            "il y a le travail sur {topic} du dernier sprint a finir",
            "{topic} etait dans notre plan de sprint, travaillons dessus",
        ],
        "es": [
            "continuemos con {topic} que discutimos ayer",
            "hay que terminar el trabajo de {topic} del sprint pasado",
            "{topic} estaba en nuestro plan de sprint, trabajemos en eso",
        ],
        "pt": [
            "vamos continuar com {topic} que discutimos ontem",
            "tem o trabalho de {topic} do sprint passado pra terminar",
            "{topic} estava no plano do sprint, vamos trabalhar nisso",
        ],
        "ru": [
            "prodolzhim s {topic} o kotorom govorili vchera",
            "est rabota po {topic} s proshlogo sprinta, nado zavershit",
            "{topic} byl v plane sprinta, davaj zajmemsja",
        ],
        "ja": [
            "{topic} no kinou no tsuzuki wo shiyou",
            "mae no supurinto no {topic} wo owarasenai to",
            "supurinto keikaku ni {topic} ga atta, sore wo yarou",
        ],
        "zh": [
            "women jixu zuotian taolun de {topic}",
            "shang ge chongci de {topic} gongzuo yao wancheng",
            "{topic} zai women de chongci jihua zhong, kaishi ba",
        ],
        "ko": [
            "{topic} eoje iyagihan geo gyesok habnida",
            "jinan seupeurinteu {topic} jageop kkeutnaeyahabnida",
            "{topic} i seupeurinteu gyehoege isseoyo, geu jageop habnida",
        ],
    },
}

# Urgency eklemeleri

URGENCY_SUFFIXES = {
    "tr": [
        "hemen",
        "acil",
        "simdi",
        "hadi",
        "bi el at",
        "dur yapiyom",
        "lutfen",
        "bekletme",
        "hizlica",
    ],
    "en": [
        "now",
        "asap",
        "quickly",
        "hurry",
        "right away",
        "urgent",
        "please",
        "don't delay",
        "fast",
    ],
    "de": ["jetzt", "sofort", "schnell", "dringend", "bitte", "eilig"],
    "fr": ["maintenant", "urgent", "vite", "rapidement", "tout de suite", "s'il te plait"],
    "es": ["ahora", "urgente", "rapido", "ya", "por favor", "de inmediato"],
    "pt": ["agora", "urgente", "rapido", "ja", "por favor", "imediatamente"],
    "ru": ["seychas", "srochno", "bystro", "nemedelenno", "pozhaluysta"],
    "ja": ["ima sugu", "kyuu de", "hayaku", "isoge", "onegai"],
    "zh": ["xianzai", "jinji", "kuai", "mashang", "qing"],
    "ko": ["jigeum", "geubhi", "ppalli", "eoseo", "juseyo"],
}

# Sistem promptu ornekleri

SYSTEM_PROMPTS = {
    "tr": [
        "Sen bir kidemli yazilim muhendisisin. Kod kalitesi ve test edilebilirlik onceligin.",
        "Frontend gelistirici olarak calis. React ve TypeScript kullan.",
        "DevOps muhendisi olarak yardim et. AWS ve Docker odakli.",
        "Sen bir guvenlik uzmanisin. OWASP standartlarina uy.",
        "Backend gelistirici olarak calis. Node.js ve PostgreSQL kullan.",
        "Sen bir teknik lidersin. Mimari kararlar ve kod kalitesi senin sorumlulugunda.",
        "Mobil gelistirici olarak calis. React Native kullan.",
        "Full-stack gelistirici olarak davran. Next.js ve Prisma kullan.",
    ],
    "en": [
        "You are a senior software engineer. Code quality and testability are your priority.",
        "Work as a frontend developer. Use React and TypeScript.",
        "Help as a DevOps engineer. Focus on AWS and Docker.",
        "You are a security specialist. Follow OWASP standards.",
        "Work as a backend developer. Use Node.js and PostgreSQL.",
        "You are a tech lead. Architecture decisions and code quality are your responsibility.",
        "Work as a mobile developer. Use React Native.",
        "Act as a full-stack developer. Use Next.js and Prisma.",
    ],
    "de": [
        "Du bist ein erfahrener Softwareingenieur. Codequalitaet hat Prioritaet.",
        "Arbeite als Frontend-Entwickler. Verwende React und TypeScript.",
        "Hilf als DevOps-Ingenieur. Fokus auf AWS und Docker.",
        "Du bist ein Sicherheitsspezialist. Folge OWASP-Standards.",
    ],
    "fr": [
        "Tu es un ingenieur logiciel senior. La qualite du code est ta priorite.",
        "Travaille comme developpeur frontend. Utilise React et TypeScript.",
        "Aide comme ingenieur DevOps. Focus sur AWS et Docker.",
        "Tu es un specialiste en securite. Suis les standards OWASP.",
    ],
    "es": [
        "Eres un ingeniero de software senior. La calidad del codigo es tu prioridad.",
        "Trabaja como desarrollador frontend. Usa React y TypeScript.",
        "Ayuda como ingeniero DevOps. Enfocate en AWS y Docker.",
    ],
    "pt": [
        "Voce e um engenheiro de software senior. Qualidade do codigo e sua prioridade.",
        "Trabalhe como desenvolvedor frontend. Use React e TypeScript.",
        "Ajude como engenheiro DevOps. Foco em AWS e Docker.",
    ],
    "ru": [
        "Ty opytnyj inzhener-programmist. Kachestvo koda — tvoj prioritet.",
        "Rabotaj kak frontend-razrabotchik. Ispolzuj React i TypeScript.",
        "Pomogi kak DevOps-inzhener. Fokus na AWS i Docker.",
    ],
    "ja": [
        "Anata wa shinia sofutouea enjinia desu. Koodo no hinshitsu ga yuusen desu.",
        "Furontendo kaihatsusha toshite hataraku. React to TypeScript wo tsukau.",
    ],
    "zh": [
        "Ni shi yiwei gaoji ruanjian gongchengshi. Daima zhiliang shi ni de youxian shixiang.",
        "Zuowei qianduan kaifazhe gongzuo. Shiyong React he TypeScript.",
    ],
    "ko": [
        "Dangsin-eun sinieo sopeuteuweeeo enjinieo ibnida. kodeu pumjiri useon suhang sahangibnida.",
        "peulonteu endeu gaebaljalo ilhabnida. React wa TypeScript sayong.",
    ],
}

# Proje baglami ornekleri

PROJECT_CONTEXTS = {
    "tr": [
        "Proje: e-ticaret platformu (Next.js + Prisma + PostgreSQL). Monorepo yapisi, Turborepo ile yonetiliyor.",
        "Proje: SaaS dashboard uygulamasi (React + Express + MongoDB). Microservice mimarisi.",
        "Proje: Mobil uygulama backend'i (FastAPI + SQLAlchemy + Redis). REST API.",
        "Proje: Acik kaynak kutuphane (TypeScript). npm'de yayinlaniyor, 2k+ yildiz.",
        "Proje: Kurumsal CRM sistemi (Angular + .NET Core + SQL Server). Legacy kod modernizasyonu.",
        "Proje: IoT veri isleme platformu (Python + Kafka + InfluxDB). Gercek zamanli veri akisi.",
    ],
    "en": [
        "Project: e-commerce platform (Next.js + Prisma + PostgreSQL). Monorepo managed with Turborepo.",
        "Project: SaaS dashboard app (React + Express + MongoDB). Microservice architecture.",
        "Project: Mobile app backend (FastAPI + SQLAlchemy + Redis). REST API.",
        "Project: Open source library (TypeScript). Published on npm, 2k+ stars.",
        "Project: Enterprise CRM system (Angular + .NET Core + SQL Server). Legacy modernization.",
        "Project: IoT data processing platform (Python + Kafka + InfluxDB). Real-time data pipeline.",
    ],
    "de": [
        "Projekt: E-Commerce-Plattform (Next.js + Prisma + PostgreSQL). Monorepo mit Turborepo.",
        "Projekt: SaaS-Dashboard (React + Express + MongoDB). Microservice-Architektur.",
        "Projekt: Open-Source-Bibliothek (TypeScript). Auf npm veroeffentlicht.",
    ],
    "fr": [
        "Projet: plateforme e-commerce (Next.js + Prisma + PostgreSQL). Monorepo gere avec Turborepo.",
        "Projet: dashboard SaaS (React + Express + MongoDB). Architecture microservice.",
        "Projet: bibliotheque open source (TypeScript). Publiee sur npm.",
    ],
    "es": [
        "Proyecto: plataforma e-commerce (Next.js + Prisma + PostgreSQL). Monorepo con Turborepo.",
        "Proyecto: dashboard SaaS (React + Express + MongoDB). Arquitectura microservicios.",
    ],
    "pt": [
        "Projeto: plataforma e-commerce (Next.js + Prisma + PostgreSQL). Monorepo com Turborepo.",
        "Projeto: dashboard SaaS (React + Express + MongoDB). Arquitetura de microservicos.",
    ],
    "ru": [
        "Proekt: e-commerce platforma (Next.js + Prisma + PostgreSQL). Monorepo s Turborepo.",
        "Proekt: SaaS daschboard (React + Express + MongoDB). Microservisnaja arhitektura.",
    ],
    "ja": [
        "Purojekuto: EC purattofoomu (Next.js + Prisma + PostgreSQL). Monorepo.",
        "Purojekuto: SaaS dasshubodo (React + Express + MongoDB). Maikurosaabisusu.",
    ],
    "zh": [
        "Xiangmu: dianshang pingtai (Next.js + Prisma + PostgreSQL). Monorepo.",
        "Xiangmu: SaaS yibiao pan (React + Express + MongoDB). Weifuwu jiagou.",
    ],
    "ko": [
        "Peurojekteu: jeonsang-geolae peullaespom (Next.js + Prisma + PostgreSQL). Monorepo.",
        "Peurojekteu: SaaS daesibodeu (React + Express + MongoDB). Maikeuseobiseu.",
    ],
}

# Hafiza / gecmis etkilesim ornekleri

MEMORY_SNIPPETS = {
    "tr": [
        "Onceki konusma: Kullanici login akisinin OAuth ile degistirilmesini istedi. Google ve GitHub provider'lari eklenecek.",
        "Gecmis not: Proje PostgreSQL 15 kullaniyor, JSONB destegi onemli.",
        "Gecen seferkinden: Docker Compose dosyasi guncellendi, Redis eklendi.",
        "Kullanici tercihi: Tailwind CSS kullanilacak, styled-components degil.",
        "Bilinen sorun: API yanit suresi 2s'yi asiyor, optimizasyon lazim.",
        "Onceki karar: Test framework olarak Vitest secildi, Jest degil.",
    ],
    "en": [
        "Previous conversation: User wanted to replace the login flow with OAuth. Google and GitHub providers to be added.",
        "Past note: Project uses PostgreSQL 15, JSONB support is important.",
        "From last time: Docker Compose was updated, Redis added.",
        "User preference: Use Tailwind CSS, not styled-components.",
        "Known issue: API response time exceeds 2s, optimization needed.",
        "Previous decision: Vitest chosen as test framework, not Jest.",
    ],
    "de": [
        "Vorheriges Gespraech: Benutzer wollte den Login-Fluss durch OAuth ersetzen.",
        "Bekanntes Problem: API-Antwortzeit ueberschreitet 2s.",
        "Benutzervorliebe: Tailwind CSS verwenden, nicht styled-components.",
    ],
    "fr": [
        "Conversation precedente: L'utilisateur voulait remplacer le flux de connexion par OAuth.",
        "Probleme connu: Le temps de reponse API depasse 2s.",
        "Preference utilisateur: Utiliser Tailwind CSS, pas styled-components.",
    ],
    "es": [
        "Conversacion anterior: El usuario queria reemplazar el flujo de login con OAuth.",
        "Problema conocido: El tiempo de respuesta de la API supera los 2s.",
    ],
    "pt": [
        "Conversa anterior: O usuario queria substituir o fluxo de login por OAuth.",
        "Problema conhecido: O tempo de resposta da API ultrapassa 2s.",
    ],
    "ru": [
        "Predydushchij razgovor: Polzovatel hotel zamenit potok avtorizacii na OAuth.",
        "Izvestnaja problema: Vremja otveta API prevyshaet 2s.",
    ],
    "ja": [
        "Zenkai no kaiwa: Yuuzaa wa roguin furo wo OAuth ni henkou shitai to itta.",
        "Kichi no mondai: API ootou jikan ga 2s wo koeru.",
    ],
    "zh": [
        "Shangci duihua: Yonghu xiang ba denglu liucheng huan cheng OAuth.",
        "Yizhi wenti: API xiangying shijian chaoguole 2 miao.",
    ],
    "ko": [
        "Ijeon daehwa: Sayongjaneun login heuleumeul OAuth ro byeongyeonghago sipeo haesseumnida.",
        "Allyeojin munje: API eungdap sigani 2choreuil chogwahabnida.",
    ],
}

# Sorulan sorular havuzu

CLARIFYING_QUESTIONS = {
    "tr": [
        "Hangi framework kullaniyorsunuz?",
        "Hedef tarayici/ortam ne?",
        "Mevcut bir implementasyon var mi, yoksa sifirdan mi?",
        "Performans gereksinimleri neler?",
        "Backend dil tercihiniz ne?",
        "Bu bir greenfield proje mi yoksa mevcut koda ekleme mi?",
        "Kullanici sayisi tahmini ne kadar?",
        "CI/CD pipeline'iniz var mi?",
        "Test coverage hedefiniz ne?",
        "Hangi veritabanini kullaniyorsunuz?",
        "Deployment ortami ne (cloud, on-prem)?",
        "Mevcut bir API dokumantasyonu var mi?",
        "Ekip kac kisi?",
        "Deadline var mi?",
    ],
    "en": [
        "What framework are you using?",
        "What's the target browser/environment?",
        "Is there an existing implementation, or starting from scratch?",
        "What are the performance requirements?",
        "What's your backend language preference?",
        "Is this a greenfield project or adding to existing code?",
        "What's the estimated user count?",
        "Do you have a CI/CD pipeline?",
        "What's your target test coverage?",
        "Which database are you using?",
        "What's the deployment environment (cloud, on-prem)?",
        "Is there existing API documentation?",
        "How big is the team?",
        "Is there a deadline?",
    ],
    "de": [
        "Welches Framework verwenden Sie?",
        "Was ist die Zielumgebung?",
        "Gibt es eine bestehende Implementierung?",
        "Welche Leistungsanforderungen gibt es?",
        "Welche Datenbank verwenden Sie?",
    ],
    "fr": [
        "Quel framework utilisez-vous?",
        "Quel est l'environnement cible?",
        "Y a-t-il une implementation existante?",
        "Quelles sont les exigences de performance?",
        "Quelle base de donnees utilisez-vous?",
    ],
    "es": [
        "Que framework estan usando?",
        "Cual es el entorno objetivo?",
        "Hay una implementacion existente?",
        "Cuales son los requisitos de rendimiento?",
    ],
    "pt": [
        "Qual framework estao usando?",
        "Qual e o ambiente alvo?",
        "Existe uma implementacao existente?",
        "Quais sao os requisitos de desempenho?",
    ],
    "ru": [
        "Kakoj frejmvork vy ispolzuete?",
        "Kakaja celevaja sreda?",
        "Est sushchestvujuschaja realizacija?",
        "Kakie trebovanija k proizvoditelnosti?",
    ],
    "ja": [
        "Dono fureemuwaku wo tsukatte imasu ka?",
        "Taagetto kankyou wa nani desu ka?",
        "Kison no jissou wa arimasu ka?",
    ],
    "zh": [
        "Nimen shiyong shenme kuangjia?",
        "Mubiao huanjing shi shenme?",
        "You xianyou de shixian ma?",
    ],
    "ko": [
        "Eoneu peuleim-weokeu sayonghago isseumnigga?",
        "Mokpyo hwangyeongi mueosimnikka?",
        "Gijeon guhyeoni isseumnigga?",
    ],
}

# Cikti yapilandirma blok sablonlari (archetype'lar)

SECTION_LABELS = {
    "tr": {
        "task": "Gorev",
        "goal": "Hedef",
        "context": "Baglam",
        "scope": "Kapsam",
        "constraints": "Kisitlar",
        "acceptance": "Kabul kriterleri",
        "format": "Cikti formati",
        "steps": "Adimlar",
        "risks": "Riskler",
        "assumptions": "Varsayimlar",
        "priority": "Oncelik",
        "dont": "Yapilmayacaklar",
        "questions": "Sorular",
        "examples": "Ornekler",
        "role": "Rol",
        "background": "Arka plan",
        "deliverables": "Teslim edilecekler",
        "timeline": "Zaman cizelgesi",
        "dependencies": "Bagimliliklar",
        "success": "Basari olcutleri",
        "alternatives": "Alternatifler",
        "notes": "Notlar",
        "refs": "Kaynaklar",
    },
    "en": {
        "task": "Task",
        "goal": "Goal",
        "context": "Context",
        "scope": "Scope",
        "constraints": "Constraints",
        "acceptance": "Acceptance criteria",
        "format": "Output format",
        "steps": "Steps",
        "risks": "Risks",
        "assumptions": "Assumptions",
        "priority": "Priority",
        "dont": "Do not",
        "questions": "Questions",
        "examples": "Examples",
        "role": "Role",
        "background": "Background",
        "deliverables": "Deliverables",
        "timeline": "Timeline",
        "dependencies": "Dependencies",
        "success": "Success metrics",
        "alternatives": "Alternatives",
        "notes": "Notes",
        "refs": "References",
    },
    "de": {
        "task": "Aufgabe",
        "goal": "Ziel",
        "context": "Kontext",
        "scope": "Umfang",
        "constraints": "Einschraenkungen",
        "acceptance": "Akzeptanzkriterien",
        "format": "Ausgabeformat",
        "steps": "Schritte",
        "risks": "Risiken",
        "assumptions": "Annahmen",
        "priority": "Prioritaet",
        "dont": "Nicht erlaubt",
        "questions": "Fragen",
        "examples": "Beispiele",
        "role": "Rolle",
        "background": "Hintergrund",
        "deliverables": "Liefergegenstande",
    },
    "fr": {
        "task": "Tache",
        "goal": "Objectif",
        "context": "Contexte",
        "scope": "Portee",
        "constraints": "Contraintes",
        "acceptance": "Criteres d'acceptation",
        "format": "Format de sortie",
        "steps": "Etapes",
        "risks": "Risques",
        "assumptions": "Hypotheses",
        "priority": "Priorite",
        "dont": "A ne pas faire",
        "questions": "Questions",
        "examples": "Exemples",
        "role": "Role",
        "background": "Contexte general",
        "deliverables": "Livrables",
    },
    "es": {
        "task": "Tarea",
        "goal": "Objetivo",
        "context": "Contexto",
        "scope": "Alcance",
        "constraints": "Restricciones",
        "acceptance": "Criterios de aceptacion",
        "format": "Formato de salida",
        "steps": "Pasos",
        "risks": "Riesgos",
        "assumptions": "Suposiciones",
        "priority": "Prioridad",
        "dont": "No hacer",
        "questions": "Preguntas",
        "examples": "Ejemplos",
        "role": "Rol",
    },
    "pt": {
        "task": "Tarefa",
        "goal": "Objetivo",
        "context": "Contexto",
        "scope": "Escopo",
        "constraints": "Restricoes",
        "acceptance": "Criterios de aceitacao",
        "format": "Formato de saida",
        "steps": "Etapas",
        "risks": "Riscos",
        "assumptions": "Suposicoes",
        "priority": "Prioridade",
        "dont": "Nao fazer",
        "questions": "Perguntas",
        "examples": "Exemplos",
        "role": "Papel",
    },
    "ru": {
        "task": "Zadacha",
        "goal": "Cel",
        "context": "Kontekst",
        "scope": "Oblast",
        "constraints": "Ogranichenija",
        "acceptance": "Kriterii priemki",
        "format": "Format vyvoda",
        "steps": "Shagi",
        "risks": "Riski",
        "assumptions": "Dopushchenija",
        "priority": "Prioritet",
        "dont": "Ne delat",
        "questions": "Voprosy",
        "examples": "Primery",
        "role": "Rol",
    },
    "ja": {
        "task": "Tasuku",
        "goal": "Mokuhyou",
        "context": "Kontekisuto",
        "scope": "Sukopu",
        "constraints": "Seiyaku",
        "acceptance": "Judaku kijun",
        "format": "Shutsuryoku keishiki",
        "steps": "Tejun",
        "risks": "Risuku",
        "assumptions": "Zentei",
        "priority": "Yuusen jun-i",
        "dont": "Kinshi jiko",
        "questions": "Shitsumon",
        "examples": "Rei",
        "role": "Yakuwari",
    },
    "zh": {
        "task": "Renwu",
        "goal": "Mubiao",
        "context": "Beijing",
        "scope": "Fanwei",
        "constraints": "Yueshu",
        "acceptance": "Yanshou biaozhun",
        "format": "Shuchu geshi",
        "steps": "Buzhou",
        "risks": "Fengxian",
        "assumptions": "Jiashe",
        "priority": "Youxian ji",
        "dont": "Jinzhi",
        "questions": "Wenti",
        "examples": "Shili",
        "role": "Jiaose",
    },
    "ko": {
        "task": "Jakop",
        "goal": "Mokpyo",
        "context": "Baegyeong",
        "scope": "Beomwi",
        "constraints": "Jeyak joseon",
        "acceptance": "Surak gijun",
        "format": "Chullyeok hyeongsik",
        "steps": "Dangyae",
        "risks": "Wiheom",
        "assumptions": "Gasseol",
        "priority": "Useon sunwi",
        "dont": "Geumji sahang",
        "questions": "Jilmun",
        "examples": "Yesi",
        "role": "Yeokhal",
    },
}


def _L(lang: str, key: str) -> str:
    labels = SECTION_LABELS.get(lang, SECTION_LABELS["en"])
    return labels.get(key, SECTION_LABELS["en"].get(key, key))


# Archetype tanimlari

ARCHETYPES = [
    "standard",
    "question_first",
    "assumption_driven",
    "scope_bounded",
    "priority_marked",
    "risk_aware",
    "context_requesting",
    "system_integrated",
    "example_driven",
    "minimal",
    "chain_of_thought",
    "role_based",
    "checklist",
    "constraint_heavy",
    "outcome_focused",
    "phased",
]


def _pick_sections(archetype: str, rng: random.Random) -> list[str]:
    """Archetype'a gore hangi bolum sirasinin kullanilacagini belirler."""
    base_maps = {
        "standard": ["task", "context", "constraints", "acceptance", "format"],
        "question_first": ["questions", "task", "context", "constraints", "acceptance"],
        "assumption_driven": ["task", "assumptions", "context", "steps", "acceptance"],
        "scope_bounded": ["task", "scope", "dont", "steps", "acceptance"],
        "priority_marked": ["task", "priority", "context", "steps", "deliverables"],
        "risk_aware": ["task", "context", "risks", "steps", "acceptance", "alternatives"],
        "context_requesting": ["questions", "task", "background", "steps", "format"],
        "system_integrated": ["role", "task", "context", "constraints", "format"],
        "example_driven": ["task", "context", "examples", "acceptance", "format"],
        "minimal": ["task", "constraints"],
        "chain_of_thought": ["task", "background", "steps", "acceptance"],
        "role_based": ["role", "task", "context", "constraints", "deliverables"],
        "checklist": ["task", "steps", "acceptance", "dont"],
        "constraint_heavy": ["task", "constraints", "dont", "format"],
        "outcome_focused": ["goal", "success", "context", "steps", "deliverables"],
        "phased": ["task", "context", "steps", "timeline", "acceptance", "risks"],
    }
    sections = list(base_maps.get(archetype, base_maps["standard"]))

    extras = [
        "notes",
        "refs",
        "dependencies",
        "alternatives",
        "format",
        "acceptance",
        "deliverables",
        "timeline",
    ]
    if rng.random() < 0.35:
        extra = rng.choice(extras)
        if extra not in sections:
            pos = rng.randint(1, len(sections))
            sections.insert(pos, extra)

    return sections


# Icerik ureticileri (her bolum icin gercekci doldurma)


def _fill_section(
    section: str, topic: str, lang: str, rng: random.Random, *, category: str = ""
) -> list[str]:
    """Bir bolumun icerigini uretir (satirlar listesi)."""
    if section == "task":
        return _task_content(topic, lang, rng, category)
    elif section == "goal":
        return _goal_content(topic, lang, rng)
    elif section == "context":
        return _context_content(topic, lang, rng)
    elif section == "scope":
        return _scope_content(topic, lang, rng)
    elif section == "constraints":
        return _constraint_content(topic, lang, rng)
    elif section == "acceptance":
        return _acceptance_content(topic, lang, rng)
    elif section == "format":
        return _format_content(topic, lang, rng)
    elif section == "steps":
        return _steps_content(topic, lang, rng)
    elif section == "risks":
        return _risk_content(topic, lang, rng)
    elif section == "assumptions":
        return _assumption_content(topic, lang, rng)
    elif section == "priority":
        return _priority_content(topic, lang, rng)
    elif section == "dont":
        return _dont_content(topic, lang, rng)
    elif section == "questions":
        pool = CLARIFYING_QUESTIONS.get(lang, CLARIFYING_QUESTIONS["en"])
        n = rng.randint(2, min(5, len(pool)))
        return rng.sample(pool, n)
    elif section == "examples":
        return _example_content(topic, lang, rng)
    elif section == "role":
        pool = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
        return [rng.choice(pool)]
    elif section == "background":
        pool = PROJECT_CONTEXTS.get(lang, PROJECT_CONTEXTS["en"])
        return [rng.choice(pool)]
    elif section == "deliverables":
        return _deliverable_content(topic, lang, rng)
    elif section == "timeline":
        return _timeline_content(topic, lang, rng)
    elif section == "dependencies":
        return _dependency_content(topic, lang, rng)
    elif section == "success":
        return _success_content(topic, lang, rng)
    elif section == "alternatives":
        return _alternative_content(topic, lang, rng)
    elif section == "notes":
        return _notes_content(topic, lang, rng)
    elif section == "refs":
        return _refs_content(topic, lang, rng)
    else:
        return [f"{topic}."]


# ---------- Bolum icerik fonksiyonlari ----------

_TASK_VERBS = {
    "tr": [
        "Implement et",
        "Olustur",
        "Gelistir",
        "Yaz",
        "Tasarla ve kodla",
        "Hazirla",
        "Kur",
        "Entegre et",
    ],
    "en": [
        "Implement",
        "Create",
        "Develop",
        "Build",
        "Design and code",
        "Set up",
        "Integrate",
        "Write",
    ],
    "de": [
        "Implementiere",
        "Erstelle",
        "Entwickle",
        "Baue",
        "Entwirf und codiere",
        "Richte ein",
        "Integriere",
    ],
    "fr": [
        "Implemente",
        "Cree",
        "Developpe",
        "Construis",
        "Concois et code",
        "Configure",
        "Integre",
    ],
    "es": [
        "Implementa",
        "Crea",
        "Desarrolla",
        "Construye",
        "Disena y codifica",
        "Configura",
        "Integra",
    ],
    "pt": [
        "Implemente",
        "Crie",
        "Desenvolva",
        "Construa",
        "Projete e codifique",
        "Configure",
        "Integre",
    ],
    "ru": [
        "Realizuj",
        "Sozdaj",
        "Razrabotaj",
        "Postroy",
        "Sprojektiruj i zakodiruj",
        "Nastroy",
        "Integriruj",
    ],
    "ja": [
        "Jissou shite",
        "Sakusei shite",
        "Kaihatsu shite",
        "Kouchiku shite",
        "Sekkei shite koodo kaite",
    ],
    "zh": ["Shixian", "Chuangjian", "Kaifa", "Goujian", "Sheji bing bianma", "Peizhi", "Jicheng"],
    "ko": [
        "Guhyeon",
        "Saengseong",
        "Gaebal",
        "Guchuk",
        "Seolgye mit koding",
        "Seoljeong",
        "Tonghap",
    ],
}

_QUALITY_ATTRS = {
    "tr": [
        "performansli",
        "test edilebilir",
        "bakimi kolay",
        "olceklenebilir",
        "guvenli",
        "temiz",
        "modular",
        "yeniden kullanilabilir",
    ],
    "en": [
        "performant",
        "testable",
        "maintainable",
        "scalable",
        "secure",
        "clean",
        "modular",
        "reusable",
    ],
    "de": ["performant", "testbar", "wartbar", "skalierbar", "sicher", "sauber", "modular"],
    "fr": ["performant", "testable", "maintenable", "scalable", "securise", "propre", "modulaire"],
    "es": ["performante", "testeable", "mantenible", "escalable", "seguro", "limpio", "modular"],
    "pt": ["performante", "testavel", "mantenivel", "escalavel", "seguro", "limpo", "modular"],
    "ru": [
        "proizvoditelnyj",
        "testiruemyj",
        "podderzhivaemyj",
        "masshtabiruemyj",
        "bezopasnyj",
        "chistyj",
        "modulnyj",
    ],
    "ja": ["koosoku", "tesuto kanou", "iji kantan", "sukeeraburu", "anzen", "kuriin", "mojuuraa"],
    "zh": ["gaoxingneng", "ke ceshi", "yi weihu", "ke kuozhan", "anquan", "zhengji", "moduhua"],
    "ko": [
        "goseongneung",
        "teseuteu ganeung",
        "yuji gwanli yongyi",
        "hwakjang ganeung",
        "boanjeok",
        "kkaekkeuthan",
        "mojulhwa",
    ],
}


def _task_content(topic: str, lang: str, rng: random.Random, category: str) -> list[str]:
    verbs = _TASK_VERBS.get(lang, _TASK_VERBS["en"])
    attrs = _QUALITY_ATTRS.get(lang, _QUALITY_ATTRS["en"])
    verb = rng.choice(verbs)
    n_attrs = rng.randint(1, 3)
    picked = rng.sample(attrs, min(n_attrs, len(attrs)))
    attr_str = ", ".join(picked)
    patterns = [
        f"{verb} {topic}.",
        f"{verb} — {attr_str} — {topic}.",
        f"{topic}: {verb}. ({attr_str})",
    ]
    return [rng.choice(patterns)]


def _goal_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    templates = {
        "tr": [
            f"{topic} islevselligini uretim ortamina hazir sekilde tamamla.",
            f"Mevcut {topic} yapisini iyilestir ve olceklenebilir hale getir.",
            f"{topic} icin surdurulebilir, test edilebilir bir cozum uret.",
        ],
        "en": [
            f"Complete {topic} functionality in a production-ready state.",
            f"Improve the existing {topic} structure and make it scalable.",
            f"Deliver a sustainable, testable solution for {topic}.",
        ],
    }
    pool = templates.get(lang, templates["en"])
    return [rng.choice(pool)]


def _context_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    project_pool = PROJECT_CONTEXTS.get(lang, PROJECT_CONTEXTS["en"])
    lines = [rng.choice(project_pool)]

    extras = {
        "tr": [
            f"Mevcut {topic} implementasyonu temel duzeyde calisiyor.",
            "Ekip 4 gelistiriciden olusuyor.",
            "Sprint sonuna kadar tamamlanmasi bekleniyor.",
            "Kod tabaninda TypeScript strict mode aktif.",
        ],
        "en": [
            f"Current {topic} implementation works at a basic level.",
            "Team consists of 4 developers.",
            "Expected to be completed by end of sprint.",
            "Codebase uses TypeScript strict mode.",
        ],
        "de": [
            f"Aktuelle {topic}-Implementierung funktioniert auf Basisniveau.",
            "Das Team besteht aus 4 Entwicklern.",
            "Soll bis zum Sprintende fertig sein.",
            "Codebase nutzt TypeScript strict mode.",
        ],
        "fr": [
            f"L'implementation actuelle de {topic} fonctionne au niveau de base.",
            "L'equipe comprend 4 developpeurs.",
            "A terminer avant la fin du sprint.",
            "La codebase utilise TypeScript strict mode.",
        ],
        "es": [
            f"La implementacion actual de {topic} funciona a nivel basico.",
            "El equipo consta de 4 desarrolladores.",
            "Se espera completar antes del fin del sprint.",
        ],
        "pt": [
            f"A implementacao atual de {topic} funciona no nivel basico.",
            "A equipe e composta por 4 desenvolvedores.",
            "Espera-se concluir ate o final do sprint.",
        ],
        "ru": [
            f"Tekushchaja realizacija {topic} rabotaet na bazovom urovne.",
            "Komanda sostoit iz 4 razrabotchikov.",
            "Ozhidaetsja zavershenie do konca sprinta.",
        ],
        "ja": [
            f"Genzai no {topic} jissou wa kihon reberu de ugoku.",
            "Chiimu wa 4-nin no kaihatsusha de kousei.",
            "Supurinto shuuryou made ni kanryoo yotei.",
        ],
        "zh": [
            f"Muqian de {topic} shixian zai jichu cengci gongzuo.",
            "Tuandui you 4 ming kaifazhe.",
            "Yuji zai chongci jieshu qian wancheng.",
        ],
        "ko": [
            f"Hyeonjae {topic} guhyeoneun gibon sujuneseo jakdonghamnida.",
            "tim-eun 4-myeong-ui gaebaljaro guseonddoeeoisseumnida.",
            "Seupeurinteu jonglyojeon wanryo yejeongibnida.",
        ],
    }
    extra_pool = extras.get(lang, extras["en"])
    n = rng.randint(1, min(3, len(extra_pool)))
    lines.extend(rng.sample(extra_pool, n))
    return lines


def _scope_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    templates = {
        "tr": {
            "in": [
                f"{topic} cekirdek islevleri",
                "Hata yonetimi",
                "Temel testler",
                "Dokumantasyon guncelleme",
            ],
            "out": [
                "Performans optimizasyonu",
                "UI/UX degisiklikleri",
                "Veritabani sema degisiklikleri",
                "Ucuncu parti entegrasyonlar",
            ],
        },
        "en": {
            "in": [
                f"{topic} core functionality",
                "Error handling",
                "Basic tests",
                "Documentation update",
            ],
            "out": [
                "Performance optimization",
                "UI/UX changes",
                "Database schema changes",
                "Third-party integrations",
            ],
        },
    }
    t = templates.get(lang, templates["en"])
    n_in = rng.randint(2, min(4, len(t["in"])))
    n_out = rng.randint(1, min(3, len(t["out"])))
    lines = [f"IN: {', '.join(rng.sample(t['in'], n_in))}"]
    lines.append(f"OUT: {', '.join(rng.sample(t['out'], n_out))}")
    return lines


def _constraint_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            "Geriye donuk uyumluluk bozulmamali.",
            "Mevcut testler kirilmamali.",
            "Yeni bagimliluk eklenmemeli.",
            "TypeScript strict mode uyumlu olmali.",
            "API sozlesmesi degismemeli.",
            "Dosya boyutu 500 satiri asmamali.",
            "Performans regresyonu kabul edilemez.",
            "Lisanslama kisitlarina dikkat edilmeli.",
        ],
        "en": [
            "Must maintain backward compatibility.",
            "Existing tests must not break.",
            "No new dependencies allowed.",
            "Must be TypeScript strict mode compatible.",
            "API contract must not change.",
            "File size should not exceed 500 lines.",
            "No performance regression acceptable.",
            "License constraints must be respected.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(2, min(5, len(pool)))
    return rng.sample(pool, n)


def _acceptance_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            f"{topic} basariyla calisiyor.",
            "Tum mevcut testler geciyor.",
            "Yeni testler eklendi ve geciyor.",
            "Kod review'dan gecti.",
            "CI/CD pipeline yesil.",
            "Dokumantasyon guncellendi.",
            "Edge case'ler handle ediliyor.",
            "Hata mesajlari anlamli.",
        ],
        "en": [
            f"{topic} works successfully.",
            "All existing tests pass.",
            "New tests added and passing.",
            "Code review approved.",
            "CI/CD pipeline green.",
            "Documentation updated.",
            "Edge cases handled.",
            "Error messages are meaningful.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(2, min(5, len(pool)))
    return rng.sample(pool, n)


def _format_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            "Degisiklikleri diff formatin da sun.",
            "Aciklama + kod ornegi olarak teslim et.",
            "Adim adim uygulama talimati.",
            "Markdown formatin da dokumante et.",
            "Sadece degisen dosyalari goster.",
        ],
        "en": [
            "Present changes as a diff.",
            "Deliver as explanation + code example.",
            "Step-by-step implementation guide.",
            "Document in markdown format.",
            "Show only changed files.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    return [rng.choice(pool)]


def _steps_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            [
                f"Mevcut {topic} kodunu analiz et.",
                "Degisiklikleri planla.",
                "Implementasyonu yap.",
                "Testleri yaz ve calistir.",
                "Review icin hazirla.",
            ],
            [
                f"{topic} icin arastirma yap.",
                "Prototip olustur.",
                "Geri bildirime gore iyilestir.",
                "Uretim ortamina hazirla.",
            ],
            [
                f"{topic} gereksinimlerini dokumante et.",
                "Teknik tasarimi olustur.",
                "Kodla.",
                "Test et.",
                "Deploy et.",
            ],
        ],
        "en": [
            [
                f"Analyze existing {topic} code.",
                "Plan the changes.",
                "Implement.",
                "Write and run tests.",
                "Prepare for review.",
            ],
            [
                f"Research {topic} approaches.",
                "Create a prototype.",
                "Refine based on feedback.",
                "Prepare for production.",
            ],
            [
                f"Document {topic} requirements.",
                "Create technical design.",
                "Code it.",
                "Test it.",
                "Deploy.",
            ],
        ],
    }
    pool = pools.get(lang, pools["en"])
    return rng.choice(pool)


def _risk_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            f"{topic} degisikligi mevcut islevselligi bozabilir.",
            "Veritabani migration'i veri kaybi riski tasiyor.",
            "Performans regresyonu olabilir.",
            "Ucuncu parti API degisiklikleri etkileyebilir.",
            "Geriye donuk uyumluluk kirilabilir.",
        ],
        "en": [
            f"{topic} changes might break existing functionality.",
            "Database migration carries data loss risk.",
            "Performance regression is possible.",
            "Third-party API changes might affect this.",
            "Backward compatibility might break.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(1, min(3, len(pool)))
    return rng.sample(pool, n)


def _assumption_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            f"Mevcut {topic} API sozlesmesi korunacak.",
            "Gelistirme ortaminda Docker mevcut.",
            "PostgreSQL 15+ kullaniliyor.",
            "Node.js 20+ mevcut.",
            "TypeScript 5+ kullaniliyor.",
            "Test framework olarak Jest/Vitest mevcut.",
        ],
        "en": [
            f"Existing {topic} API contract will be preserved.",
            "Docker is available in the dev environment.",
            "PostgreSQL 15+ is being used.",
            "Node.js 20+ is available.",
            "TypeScript 5+ is being used.",
            "Jest/Vitest is the test framework.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(2, min(4, len(pool)))
    return rng.sample(pool, n)


def _priority_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            [
                f"P0 (Kritik): {topic} cekirdek islevselligini calistir.",
                "P1 (Yuksek): Hata yonetimi ve edge case'ler.",
                "P2 (Orta): Test coverage'i artir.",
                "P3 (Dusuk): Dokumantasyon ve refactoring.",
            ],
            [
                f"ONCELIKLI: {topic} MVP'sini cikart.",
                "SONRA: Performans iyilestirmesi.",
                "ILERIDE: Ileri duzey ozellikler.",
            ],
        ],
        "en": [
            [
                f"P0 (Critical): Get {topic} core functionality working.",
                "P1 (High): Error handling and edge cases.",
                "P2 (Medium): Increase test coverage.",
                "P3 (Low): Documentation and refactoring.",
            ],
            [
                f"MUST: Ship {topic} MVP.",
                "SHOULD: Performance improvements.",
                "COULD: Advanced features.",
            ],
        ],
    }
    pool = pools.get(lang, pools["en"])
    return rng.choice(pool)


def _dont_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            "Ilgisiz kodlara dokunma.",
            "Mevcut testleri silme.",
            "Gereksiz soyutlama ekleme.",
            "API sozlesmesini bozma.",
            "Yeni bagimliluk ekleme (gerekmedikce).",
            "Console.log birakma.",
            "Magic number kullanma.",
            "Any tipini kullanma.",
        ],
        "en": [
            "Do not touch unrelated code.",
            "Do not delete existing tests.",
            "Do not add unnecessary abstractions.",
            "Do not break the API contract.",
            "Do not add new dependencies unless necessary.",
            "Do not leave console.log statements.",
            "Do not use magic numbers.",
            "Do not use the any type.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(2, min(5, len(pool)))
    return rng.sample(pool, n)


def _example_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            [
                f"Giris: kullanici {topic} sayfasini acar.",
                f"Beklenen: {topic} dogru sekilde yuklenir ve kullanilabilir.",
                "Hata durumu: Anlamli hata mesaji gosterilir.",
            ],
        ],
        "en": [
            [
                f"Input: user opens the {topic} page.",
                f"Expected: {topic} loads correctly and is usable.",
                "Error case: Meaningful error message is displayed.",
            ],
        ],
    }
    pool = pools.get(lang, pools["en"])
    return rng.choice(pool)


def _deliverable_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            f"Calisan {topic} implementasyonu.",
            "Birim + entegrasyon testleri.",
            "Guncellenmiş dokumantasyon.",
            "Degisiklik loglari.",
        ],
        "en": [
            f"Working {topic} implementation.",
            "Unit + integration tests.",
            "Updated documentation.",
            "Changelog entries.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(2, min(4, len(pool)))
    return rng.sample(pool, n)


def _timeline_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            [
                "Faz 1 (1-2 gun): Tasarim ve planlama.",
                f"Faz 2 (3-5 gun): {topic} implementasyonu.",
                "Faz 3 (1 gun): Test ve review.",
            ],
        ],
        "en": [
            [
                "Phase 1 (1-2 days): Design and planning.",
                f"Phase 2 (3-5 days): {topic} implementation.",
                "Phase 3 (1 day): Testing and review.",
            ],
        ],
    }
    pool = pools.get(lang, pools["en"])
    return rng.choice(pool)


def _dependency_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            "Veritabani semasi guncel olmali.",
            "CI/CD pipeline calisiyor olmali.",
            f"Onceki {topic} migration'lari tamamlanmis olmali.",
        ],
        "en": [
            "Database schema must be up to date.",
            "CI/CD pipeline must be operational.",
            f"Previous {topic} migrations must be completed.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(1, min(3, len(pool)))
    return rng.sample(pool, n)


def _success_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            f"{topic} %100 calisir durumda.",
            "Test coverage >%80.",
            "Yanit suresi <200ms.",
            "Sifir kritik hata.",
            "Kullanici kabul testi gecti.",
        ],
        "en": [
            f"{topic} is 100% functional.",
            "Test coverage >80%.",
            "Response time <200ms.",
            "Zero critical bugs.",
            "User acceptance test passed.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    n = rng.randint(2, min(4, len(pool)))
    return rng.sample(pool, n)


def _alternative_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            f"Alternatif A: {topic} icin hazir kutuphane kullan.",
            f"Alternatif B: {topic} icin sifirdan yaz.",
            "Karsilastirma: A daha hizli, B daha esnek.",
        ],
        "en": [
            f"Alternative A: Use an existing library for {topic}.",
            f"Alternative B: Write {topic} from scratch.",
            "Comparison: A is faster to ship, B is more flexible.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    return pool[: rng.randint(2, len(pool))]


def _notes_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    pools = {
        "tr": [
            "Eslestirme sorunu olursa Slack'ten haber ver.",
            "Buyuk degisikliklerde draft PR ac.",
            "Linting kurallarindan taviz verme.",
        ],
        "en": [
            "Ping on Slack if there's a blocker.",
            "Open a draft PR for large changes.",
            "Don't compromise on linting rules.",
        ],
    }
    pool = pools.get(lang, pools["en"])
    return [rng.choice(pool)]


def _refs_content(topic: str, lang: str, rng: random.Random) -> list[str]:
    return [
        f"docs/{topic.replace(' ', '-').lower()}.md",
        "CONTRIBUTING.md",
    ]


# Hedef-bazinda formatlayicilar


def format_claude_code(sections: list[tuple[str, list[str]]], lang: str, rng: random.Random) -> str:
    parts = []
    for key, lines in sections:
        tag = key
        content = "\n".join(f"- {line}" for line in lines)
        if key in ("questions", "steps"):
            content = "\n".join(
                f"{line_number}. {line}" for line_number, line in enumerate(lines, start=1)
            )
        parts.append(f"<{tag}>\n{content}\n</{tag}>")
    return "\n\n".join(parts)


def format_chatgpt(sections: list[tuple[str, list[str]]], lang: str, rng: random.Random) -> str:
    parts = []
    for key, lines in sections:
        label = _L(lang, key)
        if key in ("steps", "acceptance", "questions"):
            content = "\n".join(
                f"{line_number}. {line}" for line_number, line in enumerate(lines, start=1)
            )
        else:
            content = "\n".join(f"- {line}" for line in lines)
        parts.append(f"## {label}\n{content}")
    return "\n\n".join(parts)


def format_cursor(sections: list[tuple[str, list[str]]], lang: str, rng: random.Random) -> str:
    parts = []
    counter = 1
    for key, lines in sections:
        if key in ("task", "goal", "role", "background"):
            parts.append("\n".join(lines))
        elif key in ("steps",):
            for line in lines:
                parts.append(f"{counter}. {line}")
                counter += 1
        elif key == "dont":
            exclusions = ", ".join(line.lower().lstrip("- ") for line in lines)
            parts.append(f"Do not: {exclusions}.")
        elif key in ("constraints", "acceptance"):
            for line in lines:
                parts.append(f"{counter}. {line}")
                counter += 1
        else:
            label = _L(lang, key)
            parts.append(f"\n{label}:")
            for line in lines:
                parts.append(f"  - {line}")
    return "\n".join(parts)


def format_generic(sections: list[tuple[str, list[str]]], lang: str, rng: random.Random) -> str:
    variant = rng.choice(["md", "plain", "compact"])

    if variant == "md":
        return format_chatgpt(sections, lang, rng)
    elif variant == "compact":
        parts = []
        for key, lines in sections:
            label = _L(lang, key)
            parts.append(f"**{label}**: {' | '.join(lines)}")
        return "\n\n".join(parts)
    else:
        parts = []
        for key, lines in sections:
            label = _L(lang, key).upper()
            parts.append(f"{label}:")
            for line in lines:
                parts.append(f"  {line}")
            parts.append("")
        return "\n".join(parts)


FORMATTERS = {
    "claude-code": format_claude_code,
    "chatgpt": format_chatgpt,
    "codex": format_generic,
    "cursor": format_cursor,
    "deepseek": format_chatgpt,
    "gemini": format_chatgpt,
    "github-copilot": format_cursor,
    "grok": format_chatgpt,
    "generic": format_generic,
}


# Giris promptu uretici


def pick_topic(lang: str, rng: random.Random) -> tuple[str, str]:
    """Rastgele bir konu sec. (topic, category) dondurur."""
    category = rng.choice(list(TOPIC_POOLS.keys()))
    pool = TOPIC_POOLS[category]
    lang_topics = pool.get(lang, pool["en"])
    return rng.choice(lang_topics), category


def make_raw_input(
    topic: str, lang: str, style: str, rng: random.Random, *, add_urgency: bool = False
) -> str:
    pool = RAW_STYLES.get(style, RAW_STYLES["terse"])
    lang_pool = pool.get(lang, pool["en"])
    raw = rng.choice(lang_pool).format(topic=topic)

    if add_urgency:
        suffix_pool = URGENCY_SUFFIXES.get(lang, URGENCY_SUFFIXES["en"])
        raw = raw + " " + rng.choice(suffix_pool)

    return raw


# Enrichment (zenginlestirme) katmani


def maybe_add_system_prompt(rng: random.Random, lang: str) -> str | None:
    if rng.random() < 0.25:
        pool = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])
        return rng.choice(pool)
    return None


def maybe_add_memory(rng: random.Random, lang: str) -> str | None:
    if rng.random() < 0.20:
        pool = MEMORY_SNIPPETS.get(lang, MEMORY_SNIPPETS["en"])
        return rng.choice(pool)
    return None


def maybe_add_context(rng: random.Random, lang: str) -> str | None:
    if rng.random() < 0.15:
        pool = PROJECT_CONTEXTS.get(lang, PROJECT_CONTEXTS["en"])
        return rng.choice(pool)
    return None


# Tek ornek uretimi


def generate_one(lang: str, target: str, rng: random.Random) -> dict | None:
    topic, category = pick_topic(lang, rng)
    archetype = rng.choice(ARCHETYPES)

    styles = list(RAW_STYLES.keys())
    if archetype == "question_first" or archetype == "context_requesting":
        style = rng.choice(["vague", "terse"])
    elif archetype == "system_integrated":
        style = rng.choice(["descriptive", "contextual", "terse"])
    else:
        style = rng.choice(styles)

    add_urgency = rng.random() < 0.2
    raw_input = make_raw_input(topic, lang, style, rng, add_urgency=add_urgency)

    system_prompt = maybe_add_system_prompt(rng, lang)
    memory = maybe_add_memory(rng, lang)
    context = maybe_add_context(rng, lang)

    input_parts = []
    if system_prompt:
        input_parts.append(f"[system] {system_prompt}")
    if memory:
        input_parts.append(f"[memory] {memory}")
    if context:
        input_parts.append(f"[context] {context}")
    input_parts.append(raw_input)

    full_input = "\n".join(input_parts)

    sections_keys = _pick_sections(archetype, rng)
    filled_sections: list[tuple[str, list[str]]] = []
    for key in sections_keys:
        lines = _fill_section(key, topic, lang, rng, category=category)
        if lines:
            filled_sections.append((key, lines))

    if not filled_sections:
        return None

    formatter = FORMATTERS[target]
    output = formatter(filled_sections, lang, rng)

    if len(raw_input) < 6 or len(output) < 30:
        return None

    has_questions = any(k == "questions" for k, _ in filled_sections)
    has_sys = system_prompt is not None
    has_mem = memory is not None
    has_ctx = context is not None

    complexity_score = len(filled_sections)
    if has_questions:
        complexity_score += 1
    if has_sys:
        complexity_score += 1
    if has_mem:
        complexity_score += 1

    if complexity_score <= 3:
        complexity = "simple"
    elif complexity_score <= 5:
        complexity = "medium"
    else:
        complexity = "complex"

    h = hashlib.md5(f"{full_input}|{target}|{archetype}".encode()).hexdigest()[:12]
    rec_id = f"v2_{h}"

    return {
        "id": rec_id,
        "source": "synthetic_v2",
        "target": target,
        "lang": lang,
        "input": full_input,
        "output": output,
        "category": category,
        "archetype": archetype,
        "has_questions": has_questions,
        "has_system_prompt": has_sys,
        "has_context": has_ctx or has_mem,
        "complexity": complexity,
        "meta": {
            "style": style,
            "topic": topic,
        },
    }


# CLI


@click.command()
@click.option("--count", "-n", default=100_000, help="Uretilecek ornek sayisi")
@click.option("--seed", "-s", default=42, help="Rastgelelik tohumu")
@click.option("--lang", "-l", default=None, help="Tek dil filtresi (orn: tr)")
@click.option("--target", "-t", default=None, help="Tek hedef filtresi (orn: claude-code)")
@click.option("--output", "-o", default=None, help="Cikti dosya yolu")
def main(count: int, seed: int, lang: str | None, target: str | None, output: str | None) -> None:
    rng = random.Random(seed)
    out_path = Path(output) if output else OUT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)

    use_langs = [lang] if lang else LANGS
    use_targets = [target] if target else TARGETS

    seen_ids: set[str] = set()
    written = 0
    stats: dict[str, int] = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Uretiliyor...", total=count)

        with out_path.open("w", encoding="utf-8") as fh:
            attempts = 0
            max_attempts = count * 5

            while written < count and attempts < max_attempts:
                attempts += 1
                pick_lang = rng.choice(use_langs)
                pick_target = rng.choice(use_targets)

                rec = generate_one(pick_lang, pick_target, rng)
                if rec is None:
                    continue

                if rec["id"] in seen_ids:
                    continue
                seen_ids.add(rec["id"])

                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1

                lang_key = rec["lang"]
                stats[lang_key] = stats.get(lang_key, 0) + 1
                stats[f"target:{rec['target']}"] = stats.get(f"target:{rec['target']}", 0) + 1
                stats[f"arch:{rec['archetype']}"] = stats.get(f"arch:{rec['archetype']}", 0) + 1
                stats[f"cat:{rec['category']}"] = stats.get(f"cat:{rec['category']}", 0) + 1

                if rec["has_questions"]:
                    stats["with_questions"] = stats.get("with_questions", 0) + 1
                if rec["has_system_prompt"]:
                    stats["with_system_prompt"] = stats.get("with_system_prompt", 0) + 1
                if rec["has_context"]:
                    stats["with_context"] = stats.get("with_context", 0) + 1

                progress.update(task, completed=written)

    console.print(f"\n[green]{written:,} ornek yazildi -> {out_path}[/green]\n")

    console.print("[bold]Dil dagilimi:[/bold]")
    for lang_code in sorted(LANGS):
        if lang_code in stats:
            console.print(f"  {lang_code}: {stats[lang_code]:,}")

    console.print("\n[bold]Hedef dagilimi:[/bold]")
    for t in TARGETS:
        k = f"target:{t}"
        if k in stats:
            console.print(f"  {t}: {stats[k]:,}")

    console.print("\n[bold]Archetype dagilimi:[/bold]")
    for a in ARCHETYPES:
        k = f"arch:{a}"
        if k in stats:
            console.print(f"  {a}: {stats[k]:,}")

    console.print("\n[bold]Kategori dagilimi:[/bold]")
    for cat in sorted(TOPIC_POOLS.keys()):
        k = f"cat:{cat}"
        if k in stats:
            console.print(f"  {cat}: {stats[k]:,}")

    q = stats.get("with_questions", 0)
    s = stats.get("with_system_prompt", 0)
    c = stats.get("with_context", 0)
    console.print("\n[bold]Zenginlikler:[/bold]")
    console.print(f"  Sorulu: {q:,} ({100 * q / max(written, 1):.1f}%)")
    console.print(f"  Sistem promptlu: {s:,} ({100 * s / max(written, 1):.1f}%)")
    console.print(f"  Baglamli: {c:,} ({100 * c / max(written, 1):.1f}%)")


if __name__ == "__main__":
    main()
