"""100k+ sentetik egitim verisi uretici — 10 dil destegi.

Ham prompt sablonlari x hedef profiller x dil varyasyonlari x
konu kombinasyonlari ile benzersiz (input, output) ciftleri uretir.

Desteklenen diller: tr, en, de, fr, es, pt, ru, ja, zh, ko

Kullanim:
    python -m training.data.generate_synthetic --count 100000
"""

from __future__ import annotations

import json
import hashlib
import random
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console

console = Console()

OUT_PATH = Path("training/datasets/raw/synthetic.jsonl")

# ---------------------------------------------------------------------------
# Konu havuzlari — dil bazinda
# ---------------------------------------------------------------------------

TOPICS = {
    "tr": [
        "login sayfasi", "kullanici kayit formu", "sepet sistemi", "odeme modulu",
        "admin paneli", "dashboard", "bildirim servisi", "dosya yukleme",
        "arama motoru", "yorum sistemi", "chat uygulamasi", "profil sayfasi",
        "siralama algoritmasi", "filtreleme", "sayfalama", "export/import",
        "rapor olusturma", "grafik cizimi", "harita entegrasyonu", "takvim componenti",
        "drag and drop", "dark mode", "responsive tasarim", "animasyon",
        "form validasyonu", "autocomplete", "tablo componenti", "modal/dialog",
        "toast bildirimi", "progress bar", "skeleton loader", "infinite scroll",
        "websocket baglantisi", "cron job", "kuyruk sistemi", "cache katmani",
        "rate limiter", "health check", "logging sistemi", "metrik toplama",
        "A/B test altyapisi", "feature flag", "rollback mekanizmasi",
        "veritabani migration", "seed data", "unit test", "integration test",
        "CI/CD pipeline", "Docker container", "nginx reverse proxy",
        "OAuth entegrasyonu", "JWT token", "RBAC yetkilendirme",
        "GraphQL schema", "REST endpoint", "webhook handler",
        "state management", "error boundary", "lazy loading",
        "PDF olusturma", "Excel export", "CSV import",
        "blog yazisi", "teknik dokumantasyon", "API referansi",
        "hata raporu", "sunum", "e-posta taslagi", "urun aciklamasi",
        "toplanti ozeti", "proje ozeti", "test plani", "release notu",
        "performans raporu", "guvenlik degerlendirmesi", "maliyet analizi",
    ],
    "en": [
        "login page", "user registration", "shopping cart", "payment module",
        "admin panel", "dashboard layout", "notification service", "file upload",
        "search engine", "comment system", "chat application", "profile page",
        "sorting algorithm", "data filtering", "pagination", "data export",
        "report generation", "chart rendering", "map integration", "calendar widget",
        "drag and drop", "dark mode toggle", "responsive design", "CSS animation",
        "form validation", "autocomplete input", "data table", "modal dialog",
        "toast notification", "progress indicator", "skeleton loader", "infinite scroll",
        "websocket connection", "cron scheduler", "message queue", "cache layer",
        "rate limiter", "health check endpoint", "structured logging", "metrics collection",
        "A/B testing framework", "feature flags", "rollback mechanism",
        "database migration", "seed data script", "unit tests", "integration tests",
        "CI/CD pipeline", "Docker setup", "reverse proxy",
        "OAuth flow", "JWT authentication", "role-based access",
        "GraphQL schema", "REST API", "webhook handler",
        "state management", "error boundary", "lazy loading",
        "PDF generation", "spreadsheet export", "CSV parser",
        "blog post", "technical documentation", "API reference",
        "bug report", "presentation", "email draft", "product description",
        "meeting summary", "project brief", "test plan", "release notes",
        "performance report", "security assessment", "cost analysis",
    ],
    "de": [
        "Anmeldeseite", "Benutzerregistrierung", "Warenkorb", "Zahlungsmodul",
        "Admin-Panel", "Dashboard-Layout", "Benachrichtigungsdienst", "Datei-Upload",
        "Suchmaschine", "Kommentarsystem", "Chat-Anwendung", "Profilseite",
        "Sortieralgorithmus", "Datenfilterung", "Seitenumbruch", "Datenexport",
        "Berichtserstellung", "Diagramm-Rendering", "Kartenintegration",
        "Formularvalidierung", "Autovervollstaendigung", "Datentabelle",
        "Toast-Benachrichtigung", "Fortschrittsanzeige", "Endlos-Scrollen",
        "WebSocket-Verbindung", "Nachrichtenwarteschlange", "Cache-Schicht",
        "Ratenbegrenzung", "Gesundheitscheck", "Protokollierung",
        "Datenbankumstellung", "Unit-Tests", "Integrationstests",
        "CI/CD-Pipeline", "Docker-Setup", "Reverse-Proxy",
        "OAuth-Ablauf", "JWT-Authentifizierung", "Rollenbasierte Zugriffskontrolle",
        "REST-API", "GraphQL-Schema", "Webhook-Handler",
        "Zustandsverwaltung", "Fehlerbehandlung", "Lazy Loading",
        "PDF-Erstellung", "Excel-Export", "CSV-Import",
        "Blogbeitrag", "Technische Dokumentation", "Fehlerbericht",
        "Praesentation", "Projektbeschreibung", "Testplan",
    ],
    "fr": [
        "page de connexion", "inscription utilisateur", "panier d'achat", "module de paiement",
        "panneau d'administration", "tableau de bord", "service de notification", "telechargement de fichier",
        "moteur de recherche", "systeme de commentaires", "application de chat", "page de profil",
        "algorithme de tri", "filtrage de donnees", "pagination", "export de donnees",
        "generation de rapport", "rendu de graphique", "integration de carte",
        "validation de formulaire", "autocompletion", "table de donnees",
        "notification toast", "indicateur de progression", "defilement infini",
        "connexion WebSocket", "file d'attente de messages", "couche de cache",
        "limiteur de debit", "verification de sante", "journalisation",
        "migration de base de donnees", "tests unitaires", "tests d'integration",
        "pipeline CI/CD", "configuration Docker", "proxy inverse",
        "flux OAuth", "authentification JWT", "controle d'acces base sur les roles",
        "API REST", "schema GraphQL", "gestionnaire de webhook",
        "gestion d'etat", "gestion des erreurs", "chargement paresseux",
        "generation PDF", "export Excel", "import CSV",
        "article de blog", "documentation technique", "rapport de bug",
        "presentation", "description de projet", "plan de test",
    ],
    "es": [
        "pagina de inicio de sesion", "registro de usuario", "carrito de compras", "modulo de pago",
        "panel de administracion", "tablero de control", "servicio de notificaciones", "carga de archivos",
        "motor de busqueda", "sistema de comentarios", "aplicacion de chat", "pagina de perfil",
        "algoritmo de ordenamiento", "filtrado de datos", "paginacion", "exportacion de datos",
        "generacion de informes", "renderizado de graficos", "integracion de mapas",
        "validacion de formularios", "autocompletado", "tabla de datos",
        "notificacion emergente", "indicador de progreso", "desplazamiento infinito",
        "conexion WebSocket", "cola de mensajes", "capa de cache",
        "limitador de velocidad", "verificacion de estado", "registro de eventos",
        "migracion de base de datos", "pruebas unitarias", "pruebas de integracion",
        "pipeline CI/CD", "configuracion Docker", "proxy inverso",
        "flujo OAuth", "autenticacion JWT", "control de acceso basado en roles",
        "API REST", "esquema GraphQL", "manejador de webhooks",
        "gestion de estado", "manejo de errores", "carga diferida",
        "generacion de PDF", "exportacion Excel", "importacion CSV",
        "articulo de blog", "documentacion tecnica", "informe de errores",
        "presentacion", "descripcion de proyecto", "plan de pruebas",
    ],
    "pt": [
        "pagina de login", "cadastro de usuario", "carrinho de compras", "modulo de pagamento",
        "painel administrativo", "dashboard", "servico de notificacao", "upload de arquivo",
        "motor de busca", "sistema de comentarios", "aplicacao de chat", "pagina de perfil",
        "algoritmo de ordenacao", "filtragem de dados", "paginacao", "exportacao de dados",
        "geracao de relatorio", "renderizacao de grafico", "integracao de mapa",
        "validacao de formulario", "autocompletar", "tabela de dados",
        "notificacao toast", "indicador de progresso", "rolagem infinita",
        "conexao WebSocket", "fila de mensagens", "camada de cache",
        "limitador de taxa", "verificacao de saude", "registro de logs",
        "migracao de banco de dados", "testes unitarios", "testes de integracao",
        "pipeline CI/CD", "configuracao Docker", "proxy reverso",
        "fluxo OAuth", "autenticacao JWT", "controle de acesso baseado em papeis",
        "API REST", "schema GraphQL", "manipulador de webhook",
        "gerenciamento de estado", "tratamento de erros", "carregamento lazy",
        "geracao de PDF", "exportacao Excel", "importacao CSV",
    ],
    "ru": [
        "stranica vhoda", "registracija polzovatelja", "korzina pokupok", "modul oplaty",
        "admin-panel", "panel upravlenija", "servis uvedomlenij", "zagruzka fajlov",
        "poiskovyj dvizhok", "sistema kommentariev", "chat-prilozhenie", "stranica profilja",
        "algoritm sortirovki", "filtracija dannyh", "paginacija", "eksport dannyh",
        "generacija otchetov", "otrisovka grafikov", "integracija kart",
        "validacija formy", "avtozapolnenie", "tablica dannyh",
        "vsplyvajuschee uvedomlenie", "indikator progressa", "beskonechnaja prokrutka",
        "WebSocket-soedinenie", "ochered soobschenij", "sloj keshirovanija",
        "ogranichitel skorosti", "proverka zdorovja", "zhurnalirovanie",
        "migracija bazy dannyh", "modul'nye testy", "integracionnye testy",
        "CI/CD konvejer", "nastrojka Docker", "obratnyj proksi",
        "potok OAuth", "autentifikacija JWT", "rolevoj kontrol dostupa",
        "REST API", "skhema GraphQL", "obrabotchik webhookov",
        "upravlenie sostojaniem", "obrabotka oshibok", "lenivaja zagruzka",
        "generacija PDF", "eksport Excel", "import CSV",
    ],
    "ja": [
        "roguinpeeji", "yuuzaa touroku", "shopingu kaato", "shiharai mojuuru",
        "kanri paneru", "dasshubodo", "tsuuchi saabisu", "fairu appuroodo",
        "kensaku enjin", "komento shisutemu", "chatto apuri", "purofiru peeji",
        "sooto arugorizumu", "deeta firutaringu", "pejinaeshon", "deeta ekusupooto",
        "repooto sakusei", "chaato rendanringu", "chizu tougou",
        "foomu barideshon", "ootokomplito", "deeta teeburu",
        "toosuto tsuuchi", "puroguresu hyouji", "mugen sukurooru",
        "WebSocket setsuzoku", "messeeji kyuu", "kyasshu reiyaa",
        "reeto rimitaa", "herusu chekku", "rogingu",
        "deetabeesu maigreeshon", "yunitto tesuto", "tougou tesuto",
        "CI/CD paipurain", "Docker settoappu", "ribaasu purokishi",
        "OAuth nagare", "JWT ninshou", "rooru beisu akusesu seigyo",
        "REST API", "GraphQL sukiima", "webhook handoraa",
    ],
    "zh": [
        "denglu yemian", "yonghu zhuce", "gouwu che", "zhifu mokuai",
        "guanli mianban", "yibiao pan", "tongzhi fuwu", "wenjian shangchuan",
        "sousuo yinqing", "pinglun xitong", "liaotian yingyong", "geren ziliao ye",
        "paixu suanfa", "shuju guolv", "fenye", "shuju daochu",
        "baogao shengcheng", "tubiao xuanran", "ditu jicheng",
        "biaodan yanzheng", "zidong wancheng", "shuju biao",
        "tanchu tongzhi", "jindu zhibiao", "wuxian gundong",
        "WebSocket lianjie", "xiaoxi duilie", "huancun ceng",
        "sudu xianzhi", "jiankang jiancha", "rizhi jilu",
        "shujuku qianyi", "danwei ceshi", "jicheng ceshi",
        "CI/CD liushuixian", "Docker peizhi", "fan xiang daili",
        "OAuth liucheng", "JWT renzheng", "jiyu jiaose de fangwen kongzhi",
        "REST API", "GraphQL jiagou", "webhook chuliqì",
    ],
    "ko": [
        "roguin peiji", "sayongja deungnok", "jangbaguni", "gyeolche modul",
        "gwanli paeneol", "daesibodeu", "alrim seobiseu", "pail eoplodeu",
        "geomsal enjin", "daetgeul siseutem", "chaeting aep", "peuropil peiji",
        "jeongryeol algorijeum", "deiteo pilteoring", "peijineisyeon", "deiteo naebonaegi",
        "bogoseo saengseong", "chateu rendyeoring", "jido tonghap",
        "pom yuhyoseong geomsa", "jadong wanseong", "deiteo teibuel",
        "toseuteu alrim", "jinhang pyosi", "muhanjeongseo seukeulol",
        "WebSocket yeongyeol", "mesiji kyu", "kaesi gyeye",
        "soddo jeghan", "sangtae hwanin", "roging",
        "deiteobiseu maigeuresyeon", "yunit teseuteu", "tonghap teseuteu",
        "CI/CD paipeurain", "Docker seoljeong", "yeog-banghyang peuloksi",
        "OAuth heuleum", "JWT injeung", "yeokhal giban jeopgeun jegeo",
        "REST API", "GraphQL seukima", "webhook haendeuleo",
    ],
}

# ---------------------------------------------------------------------------
# Ham prompt sablonlari — dil bazinda
# ---------------------------------------------------------------------------

RAW_TEMPLATES = {
    "tr": [
        "{topic} yap", "{topic} ekle", "{topic} duzelt", "{topic} olustur",
        "{topic} hazirla", "bana {topic} lazim", "{topic} calismiyor",
        "{topic} patladi duzelt", "{topic} cok yavas", "{topic} optimize et",
        "{topic} refactor et", "su {topic} bozuk", "{topic} icin test yaz",
        "{topic} kaldir", "{topic} guncelle", "{topic} temizle",
        "{topic} basitlestir", "{topic} guvenli hale getir",
        "{topic} icin dokuman yaz", "bi {topic} gerekiyor acil",
        "{topic} nasil yapilir", "{topic} hata veriyor bak",
        "{topic} kodu cok cirkin", "hizlica {topic} at",
        "{topic} entegre et", "{topic} deploy et", "{topic} kontrol et",
        "{topic} debug et", "{topic} sifirdan yaz", "{topic} tasarla",
        "{topic} planla", "{topic} bagla", "{topic} icin ornek ver",
    ],
    "en": [
        "make {topic}", "add {topic}", "fix {topic}", "create {topic}",
        "build {topic}", "I need {topic}", "{topic} is broken",
        "{topic} crashed fix it", "{topic} is too slow", "optimize {topic}",
        "refactor {topic}", "the {topic} is buggy", "write tests for {topic}",
        "remove {topic}", "update {topic}", "clean up {topic}",
        "simplify {topic}", "secure {topic}", "write docs for {topic}",
        "need {topic} asap", "how to do {topic}", "{topic} throws errors",
        "{topic} code is messy", "quickly set up {topic}",
        "integrate {topic}", "deploy {topic}", "review {topic}",
        "debug {topic}", "write {topic} from scratch", "design {topic}",
        "plan {topic}", "connect {topic}", "give example of {topic}",
    ],
    "de": [
        "{topic} erstellen", "{topic} hinzufuegen", "{topic} reparieren",
        "{topic} bauen", "ich brauche {topic}", "{topic} funktioniert nicht",
        "{topic} ist abgestuerzt", "{topic} ist zu langsam", "{topic} optimieren",
        "{topic} umstrukturieren", "{topic} ist fehlerhaft", "Tests fuer {topic} schreiben",
        "{topic} entfernen", "{topic} aktualisieren", "{topic} bereinigen",
        "{topic} vereinfachen", "{topic} absichern", "Doku fuer {topic} schreiben",
        "brauche {topic} dringend", "wie macht man {topic}",
        "{topic} wirft Fehler", "{topic} Code ist chaotisch",
        "{topic} schnell einrichten", "{topic} integrieren", "{topic} deployen",
        "{topic} ueberpruefen", "{topic} debuggen", "{topic} von Grund auf schreiben",
        "{topic} entwerfen", "{topic} planen",
    ],
    "fr": [
        "creer {topic}", "ajouter {topic}", "corriger {topic}",
        "construire {topic}", "j'ai besoin de {topic}", "{topic} ne fonctionne pas",
        "{topic} a plante", "{topic} est trop lent", "optimiser {topic}",
        "refactoriser {topic}", "{topic} est buggue", "ecrire des tests pour {topic}",
        "supprimer {topic}", "mettre a jour {topic}", "nettoyer {topic}",
        "simplifier {topic}", "securiser {topic}", "ecrire la doc pour {topic}",
        "besoin de {topic} urgent", "comment faire {topic}",
        "{topic} lance des erreurs", "le code de {topic} est sale",
        "configurer {topic} rapidement", "integrer {topic}", "deployer {topic}",
        "verifier {topic}", "debugger {topic}", "ecrire {topic} de zero",
        "concevoir {topic}", "planifier {topic}",
    ],
    "es": [
        "crear {topic}", "agregar {topic}", "arreglar {topic}",
        "construir {topic}", "necesito {topic}", "{topic} no funciona",
        "{topic} se cayo", "{topic} es muy lento", "optimizar {topic}",
        "refactorizar {topic}", "{topic} tiene errores", "escribir tests para {topic}",
        "eliminar {topic}", "actualizar {topic}", "limpiar {topic}",
        "simplificar {topic}", "asegurar {topic}", "escribir docs para {topic}",
        "necesito {topic} urgente", "como hacer {topic}",
        "{topic} lanza errores", "el codigo de {topic} es un desastre",
        "configurar {topic} rapido", "integrar {topic}", "desplegar {topic}",
        "revisar {topic}", "depurar {topic}", "escribir {topic} desde cero",
        "disenar {topic}", "planificar {topic}",
    ],
    "pt": [
        "criar {topic}", "adicionar {topic}", "corrigir {topic}",
        "construir {topic}", "preciso de {topic}", "{topic} nao funciona",
        "{topic} travou", "{topic} esta muito lento", "otimizar {topic}",
        "refatorar {topic}", "{topic} esta com bug", "escrever testes para {topic}",
        "remover {topic}", "atualizar {topic}", "limpar {topic}",
        "simplificar {topic}", "proteger {topic}", "escrever docs para {topic}",
        "preciso de {topic} urgente", "como fazer {topic}",
        "{topic} da erro", "o codigo do {topic} esta bagunçado",
        "configurar {topic} rapido", "integrar {topic}", "fazer deploy de {topic}",
        "revisar {topic}", "debugar {topic}", "escrever {topic} do zero",
        "projetar {topic}", "planejar {topic}",
    ],
    "ru": [
        "sdelaj {topic}", "dobav {topic}", "pochini {topic}",
        "sozdaj {topic}", "mne nuzhno {topic}", "{topic} ne rabotaet",
        "{topic} slomalsja", "{topic} slishkom medlennyj", "optimiziruj {topic}",
        "refaktoriruj {topic}", "{topic} gljuchit", "napishi testy dlja {topic}",
        "uberi {topic}", "obnovi {topic}", "pochisty {topic}",
        "uprosti {topic}", "obezopas {topic}", "napishi doku dlja {topic}",
        "nuzhno {topic} srochno", "kak sdelat {topic}",
        "{topic} vydaet oshibki", "kod {topic} uzhasen",
        "bystro nastroy {topic}", "integriruj {topic}", "zadeloj {topic}",
        "prover {topic}", "otladj {topic}", "napishi {topic} s nulja",
        "sprojektiruj {topic}", "splaniruj {topic}",
    ],
    "ja": [
        "{topic} wo tsukutte", "{topic} wo tsuika shite", "{topic} wo naoshite",
        "{topic} wo sakusei shite", "{topic} ga hitsuyou", "{topic} ga ugokimasen",
        "{topic} ga kurasshu shita", "{topic} ga osoi", "{topic} wo saitekika shite",
        "{topic} wo rifakutaringu shite", "{topic} ni bagu ga aru",
        "{topic} no tesuto wo kaite", "{topic} wo sakujo shite",
        "{topic} wo kooshin shite", "{topic} wo seiri shite",
        "{topic} wo kantan ni shite", "{topic} wo anzen ni shite",
        "{topic} no doku wo kaite", "{topic} ga kyuuyo hitsuyou",
        "{topic} no yarikata", "{topic} ga eraa wo dasu",
        "{topic} no koodo ga kitanai", "{topic} wo sassoku settoappu shite",
        "{topic} wo tougou shite", "{topic} wo deburoi shite",
        "{topic} wo rebyu shite", "{topic} wo debaggu shite",
        "{topic} wo zero kara kaite", "{topic} wo sekkei shite",
    ],
    "zh": [
        "zuo {topic}", "tianjia {topic}", "xiufu {topic}",
        "chuangjian {topic}", "wo xuyao {topic}", "{topic} huaile",
        "{topic} bengkui le", "{topic} tai man le", "youhua {topic}",
        "chongfou {topic}", "{topic} you bug", "wei {topic} xie ceshi",
        "shanchu {topic}", "gengxin {topic}", "qingli {topic}",
        "jianhua {topic}", "jiagu {topic}", "wei {topic} xie wendang",
        "jiji xuyao {topic}", "zenme zuo {topic}",
        "{topic} baocu", "{topic} daima hen luan",
        "kuaisu shezhi {topic}", "jicheng {topic}", "bushu {topic}",
        "jiancha {topic}", "tiaoshi {topic}", "congcou xie {topic}",
        "sheji {topic}", "guihua {topic}",
    ],
    "ko": [
        "{topic} mandeulgi", "{topic} chuga", "{topic} gochigi",
        "{topic} saengseong", "{topic} ga pilyohabnida", "{topic} i jakdonghaji anseumnida",
        "{topic} i chungdol haesseumnida", "{topic} i neomu neurimnida",
        "{topic} choejeoghwa", "{topic} ripaektoring",
        "{topic} e beogeu isseoyo", "{topic} teseuteu jakseonghagi",
        "{topic} sakje", "{topic} eobdeiteu", "{topic} jeongri",
        "{topic} dansunh wa", "{topic} boanhwa", "{topic} munseo jakseonghagi",
        "{topic} geubhi pilyohabnida", "{topic} eotteoke hanaayo",
        "{topic} eleo balsaeng", "{topic} kodeu eojileowoyo",
        "{topic} ppalli seoljeong", "{topic} tonghap", "{topic} baepho",
        "{topic} geomto", "{topic} dibeogeu", "{topic} cheobuuteo jakseonghagi",
        "{topic} seolgye", "{topic} gyehoek",
    ],
}

# ---------------------------------------------------------------------------
# Urgency suffixes per language
# ---------------------------------------------------------------------------

URGENCY = {
    "tr": ["hemen", "acil", "lutfen", "simdi", "hadi", "bi el at"],
    "en": ["now", "asap", "please", "quickly", "hurry", "right away"],
    "de": ["jetzt", "sofort", "bitte", "schnell", "dringend"],
    "fr": ["maintenant", "urgent", "s'il te plait", "vite", "rapidement"],
    "es": ["ahora", "urgente", "por favor", "rapido", "ya"],
    "pt": ["agora", "urgente", "por favor", "rapido", "ja"],
    "ru": ["seychas", "srochno", "pozhaluysta", "bystro", "nemedelenno"],
    "ja": ["ima sugu", "kyuu de", "onegai", "hayaku", "isoge"],
    "zh": ["xianzai", "jinji", "qing", "kuai", "mashang"],
    "ko": ["jigeum", "geubhi", "juseyo", "ppalli", "eoseo"],
}

# ---------------------------------------------------------------------------
# Goal templates per language
# ---------------------------------------------------------------------------

GOAL_TEMPLATES = {
    "tr": [
        "{topic} fonksiyonelligini ekle.",
        "{topic} bilesenini olustur ve entegre et.",
        "Mevcut {topic} implementasyonundaki hatayi gider.",
        "{topic} performansini iyilestir.",
        "{topic} kodunu yeniden yapilandir.",
        "{topic} icin kapsamli testler yaz.",
        "{topic} yapilandirmasini guncelle.",
        "{topic} guvenlik acigini kapat.",
        "{topic} dokumantasyonunu hazirla.",
        "{topic} entegrasyonunu tamamla.",
        "{topic} altyapisini kur.",
        "{topic} hata yonetimini iyilestir.",
        "Eksik {topic} ozelligini tamamla.",
        "{topic} icin monitoring ekle.",
    ],
    "en": [
        "Add {topic} functionality.",
        "Create and integrate the {topic} component.",
        "Fix the bug in the existing {topic} implementation.",
        "Improve {topic} performance.",
        "Refactor the {topic} code for readability.",
        "Write comprehensive tests for {topic}.",
        "Update the {topic} configuration.",
        "Close the {topic} security vulnerability.",
        "Prepare {topic} documentation.",
        "Complete the {topic} integration.",
        "Set up {topic} infrastructure.",
        "Improve {topic} error handling.",
        "Complete the missing {topic} feature.",
        "Add monitoring for {topic}.",
    ],
    "de": [
        "{topic}-Funktionalitaet hinzufuegen.",
        "{topic}-Komponente erstellen und integrieren.",
        "Den Fehler in der {topic}-Implementierung beheben.",
        "{topic}-Leistung verbessern.",
        "{topic}-Code fuer Lesbarkeit umstrukturieren.",
        "Umfassende Tests fuer {topic} schreiben.",
        "{topic}-Konfiguration aktualisieren.",
        "{topic}-Sicherheitsluecke schliessen.",
        "{topic}-Dokumentation vorbereiten.",
        "{topic}-Integration abschliessen.",
        "{topic}-Infrastruktur einrichten.",
        "{topic}-Fehlerbehandlung verbessern.",
    ],
    "fr": [
        "Ajouter la fonctionnalite {topic}.",
        "Creer et integrer le composant {topic}.",
        "Corriger le bug dans l'implementation {topic}.",
        "Ameliorer les performances de {topic}.",
        "Refactoriser le code {topic} pour la lisibilite.",
        "Ecrire des tests complets pour {topic}.",
        "Mettre a jour la configuration {topic}.",
        "Combler la faille de securite {topic}.",
        "Preparer la documentation {topic}.",
        "Terminer l'integration {topic}.",
        "Mettre en place l'infrastructure {topic}.",
        "Ameliorer la gestion des erreurs {topic}.",
    ],
    "es": [
        "Agregar funcionalidad de {topic}.",
        "Crear e integrar el componente {topic}.",
        "Corregir el error en la implementacion de {topic}.",
        "Mejorar el rendimiento de {topic}.",
        "Refactorizar el codigo de {topic}.",
        "Escribir pruebas completas para {topic}.",
        "Actualizar la configuracion de {topic}.",
        "Cerrar la vulnerabilidad de seguridad de {topic}.",
        "Preparar la documentacion de {topic}.",
        "Completar la integracion de {topic}.",
        "Configurar la infraestructura de {topic}.",
        "Mejorar el manejo de errores de {topic}.",
    ],
    "pt": [
        "Adicionar funcionalidade de {topic}.",
        "Criar e integrar o componente {topic}.",
        "Corrigir o bug na implementacao de {topic}.",
        "Melhorar o desempenho de {topic}.",
        "Refatorar o codigo de {topic}.",
        "Escrever testes abrangentes para {topic}.",
        "Atualizar a configuracao de {topic}.",
        "Fechar a vulnerabilidade de seguranca de {topic}.",
        "Preparar a documentacao de {topic}.",
        "Completar a integracao de {topic}.",
        "Configurar a infraestrutura de {topic}.",
        "Melhorar o tratamento de erros de {topic}.",
    ],
    "ru": [
        "Dobavit funkcionalnost {topic}.",
        "Sozdat i integrirovat komponent {topic}.",
        "Ispravit bag v realizacii {topic}.",
        "Uluchshit proizvoditelnost {topic}.",
        "Provesti refaktoring koda {topic}.",
        "Napisat kompleksnye testy dlja {topic}.",
        "Obnovit konfiguracju {topic}.",
        "Zakryt ujazvimost v bezopasnosti {topic}.",
        "Podgotovit dokumentaciju {topic}.",
        "Zavershit integraciju {topic}.",
        "Nastroit infrastrukturu {topic}.",
        "Uluchshit obrabotku oshibok {topic}.",
    ],
    "ja": [
        "{topic} no kinoo wo tsuika suru.",
        "{topic} konpoonento wo sakusei shi tougou suru.",
        "{topic} jissou no bagu wo shuusei suru.",
        "{topic} no pafoomansu wo kaizen suru.",
        "{topic} koodo wo rifakutaringu suru.",
        "{topic} no taiou-teki na tesuto wo kaku.",
        "{topic} no settei wo kooshin suru.",
        "{topic} no sekyuriti zeijyakusei wo fusagu.",
        "{topic} no dokyumento wo junbi suru.",
        "{topic} no tougou wo kanryoo suru.",
    ],
    "zh": [
        "Tianjia {topic} gongneng.",
        "Chuangjian bing jicheng {topic} zujian.",
        "Xiufu {topic} shixian zhong de bug.",
        "Tigao {topic} xingneng.",
        "Chongfou {topic} daima yi tigao keduuxing.",
        "Wei {topic} bianxie quanmian de ceshi.",
        "Gengxin {topic} peizhi.",
        "Guanbi {topic} anquan loudong.",
        "Zhunbei {topic} wendang.",
        "Wancheng {topic} jicheng.",
    ],
    "ko": [
        "{topic} gineung chuga.",
        "{topic} keomponeonteu saengseong mit tonghap.",
        "{topic} guhyeon-ui beogeu sujeonghagi.",
        "{topic} seongneng gaeseon.",
        "{topic} kodeu ripaegeutoling.",
        "{topic} e daehan pogoaljeoin teseuteu jakseonghagi.",
        "{topic} seoljeong eobdeiteu.",
        "{topic} boan chwiyagjeom haekyeol.",
        "{topic} munseo junbi.",
        "{topic} tonghap wanryo.",
    ],
}

# ---------------------------------------------------------------------------
# Output section labels per language (for chatgpt/generic builders)
# ---------------------------------------------------------------------------

LABELS = {
    "tr": {"goal": "Hedef", "context": "Baglam", "constraints": "Kisitlar",
           "acceptance": "Kabul kriterleri", "format": "Cikti formati",
           "steps": "Adimlar"},
    "en": {"goal": "Goal", "context": "Context", "constraints": "Constraints",
           "acceptance": "Acceptance criteria", "format": "Output format",
           "steps": "Steps"},
    "de": {"goal": "Ziel", "context": "Kontext", "constraints": "Einschraenkungen",
           "acceptance": "Akzeptanzkriterien", "format": "Ausgabeformat",
           "steps": "Schritte"},
    "fr": {"goal": "Objectif", "context": "Contexte", "constraints": "Contraintes",
           "acceptance": "Criteres d'acceptation", "format": "Format de sortie",
           "steps": "Etapes"},
    "es": {"goal": "Objetivo", "context": "Contexto", "constraints": "Restricciones",
           "acceptance": "Criterios de aceptacion", "format": "Formato de salida",
           "steps": "Pasos"},
    "pt": {"goal": "Objetivo", "context": "Contexto", "constraints": "Restricoes",
           "acceptance": "Criterios de aceitacao", "format": "Formato de saida",
           "steps": "Etapas"},
    "ru": {"goal": "Cel", "context": "Kontekst", "constraints": "Ogranichenija",
           "acceptance": "Kriterii priemki", "format": "Format vyvoda",
           "steps": "Shagi"},
    "ja": {"goal": "Mokuhyou", "context": "Kontekisuto", "constraints": "Seiyaku",
           "acceptance": "Judaku kijun", "format": "Shutsuryoku keishiki",
           "steps": "Tejun"},
    "zh": {"goal": "Mubiao", "context": "Beijing", "constraints": "Yueshu",
           "acceptance": "Yanshou biaozhun", "format": "Shuchu geshi",
           "steps": "Buzhou"},
    "ko": {"goal": "Mokpyo", "context": "Baegyeong", "constraints": "Jeyak joseon",
           "acceptance": "Surak gijun", "format": "Chullyeok hyeongsik",
           "steps": "Dangyae"},
}

# ---------------------------------------------------------------------------
# Output builders
# ---------------------------------------------------------------------------

def build_claude_code_output(goal: str, topic: str, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    return f"""<task>
{goal}
</task>

<context>
- {L['steps']} 1: {topic}.
- {L['context']}.
</context>

<constraints>
- {L['constraints']}.
</constraints>

<acceptance>
- {topic}: OK.
- Tests: OK.
</acceptance>

<output_format>
- Diff.
- {L['format']}.
</output_format>"""


def build_chatgpt_output(goal: str, topic: str, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    return f"""## {L['goal']}
{goal}

## {L['context']}
- {topic}.

## {L['constraints']}
- {L['constraints']}.

## {L['acceptance']}
1. {topic}: OK.
2. {L['acceptance']}.

## {L['format']}
- Markdown."""


def build_cursor_output(goal: str, topic: str, lang: str) -> str:
    return f"""{goal}

1. Find files related to {topic}.
2. Analyze current implementation.
3. Apply changes.
4. Verify — run tests.
5. Confirm nothing broke.

Do not: change unrelated code, remove tests, add unnecessary abstractions."""


def build_generic_output(goal: str, topic: str, lang: str) -> str:
    L = LABELS.get(lang, LABELS["en"])
    return f"""## {L['goal']}
{goal}

## {L['context']}
- {topic}.

## {L['steps']}
1. Analyze {topic}.
2. Plan changes.
3. Implement.
4. Verify.

## {L['acceptance']}
1. {topic}: OK.
2. Backward compatibility.

## {L['format']}
- Summary + files."""


BUILDERS = {
    "claude-code": build_claude_code_output,
    "chatgpt": build_chatgpt_output,
    "cursor": build_cursor_output,
    "generic": build_generic_output,
}

ALL_LANGS = list(TOPICS.keys())


def make_goal(topic: str, lang: str, rng: random.Random) -> str:
    templates = GOAL_TEMPLATES.get(lang, GOAL_TEMPLATES["en"])
    return rng.choice(templates).format(topic=topic)


def make_raw_prompt(topic: str, lang: str, rng: random.Random) -> str:
    templates = RAW_TEMPLATES.get(lang, RAW_TEMPLATES["en"])
    return rng.choice(templates).format(topic=topic)


def record_id(raw: str, target: str) -> str:
    h = hashlib.md5(f"{raw}|{target}".encode()).hexdigest()[:12]
    return f"syn_{h}"


# ---------------------------------------------------------------------------
# Ana uretici
# ---------------------------------------------------------------------------

@click.command()
@click.option("--count", "-n", default=100_000, help="Uretilecek ornek sayisi")
@click.option("--seed", "-s", default=42, help="Rastgelelik tohumu")
def main(count: int, seed: int) -> None:
    rng = random.Random(seed)
    targets = list(BUILDERS.keys())

    combos = []
    for lang in ALL_LANGS:
        for topic in TOPICS[lang]:
            for target in targets:
                combos.append((lang, topic, target))

    rng.shuffle(combos)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    seen_inputs: set[str] = set()
    written = 0
    lang_counts: dict[str, int] = {}

    with OUT_PATH.open("w", encoding="utf-8") as fh:
        cycle = 0
        while written < count:
            cycle += 1
            for lang, topic, target in combos:
                if written >= count:
                    break

                raw = make_raw_prompt(topic, lang, rng)

                if cycle > 1:
                    raw = raw + " " + rng.choice(URGENCY.get(lang, URGENCY["en"]))

                input_key = f"{raw}|{target}"
                if input_key in seen_inputs:
                    continue
                seen_inputs.add(input_key)

                goal = make_goal(topic, lang, rng)
                builder = BUILDERS[target]
                output = builder(goal, topic, lang)

                if len(raw) < 8 or len(output) < 40:
                    continue

                rec = {
                    "id": record_id(raw, target),
                    "source": "synthetic",
                    "target": target,
                    "lang": lang,
                    "input": raw,
                    "output": output,
                    "meta": {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "notes": f"cycle_{cycle}",
                    },
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

                if written % 10000 == 0:
                    console.print(f"  {written:,} / {count:,}")

    console.print(f"[green]{written:,} sentetik ornek yazildi -> {OUT_PATH}[/green]")
    console.print("  Dil dagilimi:")
    for lang in sorted(lang_counts, key=lang_counts.get, reverse=True):
        console.print(f"    {lang}: {lang_counts[lang]:,}")


if __name__ == "__main__":
    main()
