"""SW Events Generator v2 — improved realism + Vercel-native."""
from __future__ import annotations
import base64, collections, datetime as dt, hashlib, json, math, random, zipfile
from io import BytesIO
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="SW Events Generator")

# ── Event type weights ──
EW = [
    ("ACTIVITY_RESUMED",28),("ACTIVITY_PAUSED",27.5),("EVENT_23",22),
    ("NOTIFICATION_INTERRUPTION",6),("NOTIFICATION_SEEN",4.5),
    ("FOREGROUND_SERVICE_START",3.2),("FOREGROUND_SERVICE_STOP",3.2),
    ("STANDBY_BUCKET_CHANGED",8),("USER_INTERACTION",1.6),
    ("SCREEN_INTERACTIVE",0.9),("SCREEN_NON_INTERACTIVE",0.8),
    ("KEYGUARD_HIDDEN",0.3),("KEYGUARD_SHOWN",0.2),("CONFIGURATION_CHANGE",0.1)
]

# ── Indonesian user hour distribution (UTC) ──
BH_INDONESIA = [
    0.040, 0.046, 0.044, 0.046, 0.044, 0.045,
    0.050, 0.055, 0.058, 0.060, 0.055, 0.050,
    0.048, 0.045, 0.042, 0.040, 0.042, 0.045,
    0.050, 0.048, 0.040, 0.035, 0.030, 0.028,
]

# ── System / bloatware packages ──
SYSTEM_APPS = [
    "com.android.settings","com.android.systemui","com.android.launcher3",
    "com.android.phone","com.android.dialer","com.android.contacts",
    "com.android.mms","com.android.email","com.android.calendar",
    "com.android.calculator2","com.android.camera2","com.android.gallery3d",
    "com.android.music","com.android.deskclock","com.android.browser",
    "com.android.providers.contacts","com.android.providers.media",
    "com.android.providers.downloads","com.android.providers.telephony",
    "com.android.providers.settings","com.android.vending","com.android.chrome",
    "com.android.nfc","com.android.bluetooth","com.android.wifi.resources",
    "com.android.inputmethod.latin","com.android.documentsui",
    "com.android.quicksearchbox","com.android.stk","com.android.stk2",
    "com.google.android.gms","com.google.android.gsf","com.google.android.feedback",
    "com.google.android.tts","com.google.android.apps.maps",
    "com.google.android.apps.photos","com.google.android.apps.docs",
    "com.google.android.gm","com.google.android.youtube",
    "com.google.android.music","com.google.android.videos",
    "com.google.android.apps.messaging","com.google.android.dialer",
    "com.google.android.contacts","com.google.android.deskclock",
    "com.google.android.calculator","com.google.android.apps.nbu.files",
    "com.google.android.apps.chromecast.app","com.google.android.apps.wellbeing",
    "com.google.android.as","com.google.android.partnersetup",
    "com.google.android.play.games","com.google.android.apps.googleassistant",
    "com.google.android.apps.turbo","com.google.ar.core",
    "com.google.android.marvin.talkback","com.google.android.configupdater",
    "com.google.android.ext.services","com.google.android.overlay.gmsconfig",
    "com.google.mainline.telemetry",
    "com.google.android.feedback","com.google.android.marvin.talkback",
    "com.google.android.apps.inputmethod.hindi","com.google.android.apps.translate",
    "com.google.android.apps.accessibility.voiceaccess","com.google.android.apps.tachyon",
    "com.google.android.apps.wearables.maestro.companion","com.google.android.apps.gmm",
    "com.google.android.apps.nbu.files","com.google.android.apps.work.oobconfig",
    "com.google.android.backuptransport","com.google.android.partnersetup",
    "com.google.android.setupwizard","com.google.android.syncadapters.contacts",
    "com.google.android.gms.setup","com.google.android.turboadapter",
    "com.google.ar.core","com.google.ar.lens",
    "com.android.traceur","com.android.vpndialogs","com.android.wallpapercropper",
    "com.android.wallpaperpicker","com.android.providers.userdictionary",
    "com.android.providers.calendar","com.android.providers.settings",
    "com.android.sharedstoragebackup","com.android.externalstorage",
    "com.android.providers.contacts","com.android.providers.downloads",
    "com.android.providers.media","com.android.providers.telephony",
    "com.android.systemui","com.android.keychain","com.android.location.fused",
    "com.android.nfc","com.android.bluetooth","com.android.shell",
    "com.android.documentsui","com.android.packageinstaller","com.android.se",
    "com.android.phone","com.android.incallui","com.android.server.telecom",
    "com.android.mms.service","com.android.calendar","com.android.deskclock",
    "com.android.calculator2","com.android.email","com.android.htmlviewer",
    "com.android.stk","com.android.wallpaper.livepicker",
    "com.samsung.android.spaymini","com.samsung.android.ardcontroller",
    "com.samsung.android.beaconmanager","com.samsung.android.service.aircommand",
    "com.samsung.android.service.stplatform","com.samsung.android.svoice",
    "com.miui.miwallpaper","com.miui.cleanmaster","com.miui.guardprovider",
    "com.miui.hybrid","com.miui.securitycore","com.miui.daemon",
    "com.oppo.speechassist","com.oppo.deepthinker","com.oppo.store",
    "com.coloros.bootreg","com.coloros.gamespace","com.coloros.operationManual",
    "com.transsion.pocketmode","com.transsion.floatbokeh","com.transsion.magicshow",
    "com.transsion.aivoice","com.transsion.XOSlauncher",    "com.transsion.compass","com.transsion.filemanager","com.transsion.soundrecorder",
    "com.transsion.weather","com.transsion.flashlight",
    "com.advan.dlauncher","com.advan.camera","com.advan.filemanager",
    "com.advan.gallery","com.advan.calculator","com.advan.clock","com.advan.weather",
    "com.vivo.weather","com.vivo.browser","com.vivo.video","com.vivo.music",
    "com.vivo.notes","com.vivo.email","com.vivo.translator","com.vivo.scanner",
    "com.realme.weather","com.realme.calculator","com.realme.clock","com.realme.compass",
    "com.realme.filemanager","com.realme.gallery","com.realme.music","com.realme.notes",
    "com.honor.calculator","com.honor.clock","com.honor.compass","om.honor.weather",
    "com.honor.filemanager","com.honor.gallery",]

SAMSUNG_SYSTEM = [
    "com.samsung.android.messaging","com.samsung.android.dialer",
    "com.samsung.android.contacts","com.samsung.android.calendar",
    "com.samsung.android.app.clock","com.samsung.android.calculator",
    "com.samsung.android.camera","com.samsung.android.gallery3d",
    "com.samsung.android.music","com.samsung.android.video",
    "com.samsung.android.email.provider","com.samsung.android.fmm",
    "com.samsung.android.game.gamehome","com.samsung.android.game.gametools",
    "com.samsung.android.ardrawing","com.samsung.android.aremoji",
    "com.samsung.android.app.routines","com.samsung.android.bixby.agent",
    "com.samsung.android.bixby.service","com.samsung.android.visionintelligence",
    "com.samsung.android.spay","com.samsung.android.mateagent",
    "com.samsung.android.app.tips","com.samsung.android.themestore",
    "com.samsung.android.icecone","com.samsung.android.forest",
    "com.samsung.android.app.sharelive","com.samsung.android.kidsinstaller",
    "com.samsung.android.app.spage","com.samsung.android.dqagent",
    "com.samsung.android.securitylogagent","com.samsung.android.mobileservice",
    "com.samsung.android.app.omcagent","com.samsung.android.samsungpass",
    "com.samsung.android.samsungpassautofill","com.samsung.android.authfw",
    "com.samsung.android.kgclient","com.samsung.android.MtpApplication",
    "com.samsung.android.server.iris","com.samsung.android.privateshare",
    "com.samsung.android.app.telephonyui","com.samsung.android.incallui",
    "com.samsung.android.da.daagent","com.samsung.android.mdx.kit",
    "com.samsung.android.wellbeing","com.samsung.android.app.galaxyfinder",
    "com.samsung.android.honeyboard","com.samsung.android.setting.multisound",
    "com.sec.android.app.launcher","com.sec.android.app.sbrowser",
    "com.sec.android.app.popupcalculator","com.sec.android.gallery3d",
    "com.sec.android.daemonapp","com.sec.android.provider.logsprovider",
    "com.sec.android.app.bluetoothtest","com.sec.android.easyMover",
    "com.sec.android.easyMover.Agent","com.sec.msc.android",
    "com.sec.android.app.camera","com.sec.android.app.myfiles",
    "com.sec.android.app.fmradio",
    "com.sec.android.widgetapp.easymodecontactswidget",
    "com.sec.android.widgetapp.digitalclock",
    "com.sec.android.provider.emergencylocation",
]

XIAOMI_SYSTEM = [
    "com.miui.home","com.miui.gallery","com.miui.player",
    "com.miui.video","com.miui.weather2","com.miui.calculator",
    "com.miui.compass","com.miui.fm","com.miui.notes",
    "com.miui.screenrecorder","com.miui.securitycenter",
    "com.miui.securitycore","com.miui.cleanmaster",
    "com.miui.personalassistant","com.miui.bugreport",
    "com.miui.mishare","com.miui.misound","com.miui.voiceassist",
    "com.miui.cloudservice","com.miui.cloudbackup","com.miui.backup",
    "com.miui.packageinstaller","com.miui.daemon","com.miui.aod",
    "com.miui.extraphoto","com.miui.mediaviewer","com.miui.contentcatcher",
    "com.miui.freeform","com.miui.guardprovider","com.miui.notification",
    "com.miui.phrase","com.miui.smsextra","com.miui.system",
    "com.miui.touchassistant","com.miui.vidaaiv4",
    "com.xiaomi.mipicks","com.xiaomi.xmsf","com.xiaomi.joyose",
    "com.xiaomi.finddevice","com.xiaomi.simactivate",
    "com.xiaomi.aiasst.service","com.xiaomi.account",
    "com.xiaomi.drivemode","com.xiaomi.payment",
    "com.xiaomi.misettings","com.xiaomi.barrage",
    "com.xiaomi.channel","com.xiaomi.shop","com.xiaomi.smarthome",
    "com.xiaomi.scanner","com.mi.android.globallauncher",
    "com.google.android.feedback","com.google.android.marvin.talkback",
    "com.google.android.apps.inputmethod.hindi","com.google.android.apps.translate",
    "com.google.android.apps.accessibility.voiceaccess","com.google.android.apps.tachyon",
    "com.google.android.apps.wearables.maestro.companion","com.google.android.apps.gmm",
    "com.google.android.apps.nbu.files","com.google.android.apps.work.oobconfig",
    "com.google.android.backuptransport","com.google.android.partnersetup",
    "com.google.android.setupwizard","com.google.android.syncadapters.contacts",
    "com.google.android.gms.setup","com.google.android.turboadapter",
    "com.google.ar.core","com.google.ar.lens",
    "com.android.traceur","com.android.vpndialogs","com.android.wallpapercropper",
    "com.android.wallpaperpicker","com.android.providers.userdictionary",
    "com.android.providers.calendar","com.android.providers.settings",
    "com.android.sharedstoragebackup","com.android.externalstorage",
    "com.android.providers.contacts","com.android.providers.downloads",
    "com.android.providers.media","com.android.providers.telephony",
    "com.android.systemui","com.android.keychain","com.android.location.fused",
    "com.android.nfc","com.android.bluetooth","com.android.shell",
    "com.android.documentsui","com.android.packageinstaller","com.android.se",
    "com.android.phone","com.android.incallui","com.android.server.telecom",
    "com.android.mms.service","com.android.calendar","com.android.deskclock",
    "com.android.calculator2","com.android.email","com.android.htmlviewer",
    "com.android.stk","com.android.wallpaper.livepicker",
    "com.samsung.android.spaymini","com.samsung.android.ardcontroller",
    "com.samsung.android.beaconmanager","com.samsung.android.service.aircommand",
    "com.samsung.android.service.stplatform","com.samsung.android.svoice",
    "com.samsung.android.widgetapp.widgetpick",
    "com.miui.miwallpaper","com.miui.cleanmaster","com.miui.guardprovider",
    "com.miui.hybrid","com.miui.securitycore","com.miui.daemon",
    "com.oppo.speechassist","com.oppo.deepthinker","com.oppo.store",
    "com.coloros.bootreg","com.coloros.gamespace","com.coloros.operationManual",
]

OPPO_SYSTEM = [
    "com.oppo.launcher","com.oppo.camera","com.oppo.gallery3d",
    "com.oppo.music","com.oppo.video","com.oppo.weather2",
    "com.oppo.calculator","com.oppo.compass","com.oppo.fmradio",
    "com.oppo.note","com.oppo.screenrecorder","com.oppo.safecenter",
    "com.oppo.cleanmaster","com.oppo.personalassistant",
    "com.oppo.bugreport","com.oppo.mishare","com.oppo.misound",
    "com.oppo.voiceassist","com.oppo.cloudservice","com.oppo.cloudbackup",
    "com.oppo.backup","com.oppo.packageinstaller","com.oppo.daemon",
    "com.oppo.aod","com.oppo.extraphoto","com.oppo.mediaviewer",
    "com.oppo.quicksearchbox",
    "com.coloros.assistant","com.coloros.athena","com.coloros.bootreg",
    "com.coloros.childrenspace","com.coloros.compass2",
    "com.coloros.deepthinker","com.coloros.encryption",
    "com.coloros.floatassistant","com.coloros.focusmode",
    "com.coloros.gamespace","com.coloros.gallery3d",
    "com.coloros.healthcheck","com.coloros.healthservice",
    "com.coloros.notificationmanager","com.coloros.ocrservice",
    "com.coloros.oppomultiapp","com.coloros.oshare",
    "com.coloros.phonemanager","com.coloros.safecenter",
    "com.coloros.safesdkproxy","com.coloros.screenshot",
    "com.coloros.securitypermission","com.coloros.smartsidebar",
    "com.coloros.soundrecorder","com.coloros.uxdesign",
    "com.coloros.weather2","com.coloros.wirelesssettings",
    "com.heytap.cloud","com.heytap.browser","com.heytap.colorfulengine",
    "com.heytap.habit.analysis","com.heytap.market","com.heytap.mcs",
    "com.heytap.pictorial","com.heytap.themestore","com.heytap.usercenter",
    "com.nearme.gamecenter","com.nearme.atlas",
    "com.google.android.turboadapter","com.google.ar.core","com.google.ar.lens",
    "com.android.traceur","com.android.vpndialogs","com.android.wallpapercropper",
    "com.android.wallpaperpicker","com.android.providers.userdictionary",
    "com.android.providers.calendar","com.android.providers.settings",
    "com.android.sharedstoragebackup","com.android.externalstorage",
    "com.android.providers.contacts","com.android.providers.downloads",
    "com.android.providers.media","com.android.providers.telephony",
    "com.android.systemui","com.android.keychain","com.android.location.fused",
    "com.android.nfc","com.android.bluetooth","com.android.shell",
    "com.android.documentsui","com.android.packageinstaller","com.android.se",
    "com.android.phone","com.android.incallui","com.android.server.telecom",
    "com.android.mms.service","com.android.calendar","com.android.deskclock",
    "com.android.calculator2","com.android.email","com.android.htmlviewer",
    "com.android.stk","com.android.wallpaper.livepicker",
    "com.google.android.webview","com.google.android.networkstack",
    "com.google.android.captiveportallogin","com.google.android.tetheringentitlement",
    "com.google.android.printservice.recommendation",
    "com.google.android.overlay.modules.ext.services",
    "com.google.android.overlay.modules.modulemetadata",
    "com.samsung.android.app.cocktailbarservice","com.samsung.android.provider.filterprovider",
    "com.samsung.android.provider.settings","com.samsung.android.samsungpass",
    "com.samsung.android.knox.attestation","com.samsung.android.forest",
    "com.samsung.android.mateagent","com.samsung.android.visionintelligence",
    "com.samsung.android.app.routines","com.samsung.android.ardrawing",
    "com.samsung.android.aremoji","com.samsung.android.app.tips",
    "com.samsung.android.wellbeing","com.samsung.android.fmm",
    "com.samsung.android.app.sharelive","com.samsung.android.icecone",
    "com.samsung.android.kidsinstaller","com.samsung.android.mobileservice",
    "com.samsung.android.samsungpassautofill","com.samsung.android.scloud",
    "com.samsung.android.smartmirroring","com.samsung.android.voc",
    "com.miui.aod","com.miui.touchassistant","com.miui.cloudservice",
    "com.miui.backup","com.miui.mishare.connectivity","com.miui.personalassistant",
    "com.miui.bugreport","com.miui.voiceassist","com.miui.extraphoto",
    "com.miui.contentcatcher","com.miui.mediaeditor","com.miui.misound",
    "com.miui.player","com.miui.screenrecorder","com.miui.virtualsim",
    "com.miui.yellowpage",
    "com.oppo.exserviceui","com.oppo.atlas","com.oppo.operationManual",
    "com.oppo.usercenter","com.oppo.powermonitor","com.oppo.screenrecorder",
    "com.oppo.securepay",
    "com.coloros.safecenter","com.coloros.assistantscreen","com.coloros.deepthinker",
    "com.coloros.healthcheck","com.coloros.oshare","com.coloros.screenrecorder",
    "com.coloros.smartsidebar",
    "com.transsion.pocketmode","com.transsion.floatbokeh","com.transsion.magicshow",
    "com.transsion.aivoice","com.transsion.XOSlauncher",    "com.transsion.compass","com.transsion.filemanager","com.transsion.soundrecorder",
    "com.transsion.weather","com.transsion.flashlight",
    "com.advan.dlauncher","com.advan.camera","com.advan.filemanager",
    "com.advan.gallery","com.advan.calculator","com.advan.clock","com.advan.weather",
    "com.google.android.feedback","com.google.android.marvin.talkback",
    "com.google.android.apps.inputmethod.hindi","com.google.android.apps.translate",
    "com.google.android.apps.accessibility.voiceaccess","com.google.android.apps.tachyon",
    "com.google.android.apps.wearables.maestro.companion","com.google.android.apps.gmm",
    "com.google.android.apps.nbu.files","com.google.android.apps.work.oobconfig",
    "com.google.android.apps.enterprise.cpanel","com.google.android.backuptransport",
    "com.google.android.partnersetup","com.google.android.setupwizard",
    "com.google.android.syncadapters.contacts","com.google.android.gms.setup",
    "com.samsung.android.spaymini","com.samsung.android.ardcontroller",
    "com.samsung.android.beaconmanager","com.samsung.android.app.cocktailbarservice",
    "com.samsung.android.service.aircommand","com.samsung.android.service.stplatform",
    "com.samsung.android.samsungpasspersonalpage","com.samsung.android.spayfw",
    "com.samsung.android.svoice","com.samsung.android.widgetapp.widgetpick",
    "com.miui.miwallpaper","com.miui.cleanmaster","com.miui.guardprovider",
    "com.miui.hybrid","com.miui.securitycore","com.miui.daemon",
    "com.oppo.speechassist","com.oppo.deepthinker","com.oppo.store",
    "com.coloros.bootreg","com.coloros.gamespace","com.coloros.operationManual",
]

INFINIX_SYSTEM = [
    "com.transsion.hilauncher","com.transsion.XOSLauncher",
    "com.transsion.microintelligence","com.transsion.soundrecorder",
    "com.transsion.XOS.chargeanim","com.transsion.XOS.weather",
    "com.transsion.XOS.compass","com.transsion.XOS.calculator",
    "com.transsion.XOS.fmradio","com.transsion.XOS.gallery3d",
    "com.transsion.XOS.music","com.transsion.XOS.video",
    "com.transsion.XOS.securitycenter","com.transsion.XOS.cleanmaster",
    "com.transsion.XOS.personalassistant","com.transsion.XOS.bugreport",
    "com.transsion.XOS.mishare","com.transsion.XOS.misound",
    "com.transsion.XOS.voiceassist","com.transsion.XOS.cloudservice",
    "com.transsion.XOS.cloudbackup","com.transsion.XOS.backup",
    "com.transsion.XOS.packageinstaller","com.transsion.XOS.daemon",
    "com.transsion.XOS.aod","com.transsion.XOS.extraphoto",
    "com.transsion.XOS.mediaviewer","com.transsion.XOS.quicksearchbox",
    "com.transsion.XOS.safecenter","com.transsion.XOS.screenshot",
    "com.transsion.XOS.soundrecorder","com.transsion.XOS.uxdesign",
    "com.transsion.XOS.weather2","com.transsion.XOS.wirelesssettings",
]

# ── Background services ──
BG_SERVICES = [
    "com.google.android.gms.policy_sidecar_aps","com.google.android.gms.feedback",
    "com.google.android.gms.icing","com.google.android.gms.nearby",
    "com.google.android.gms.persistent","com.google.android.gms.ui",
    "com.google.android.gms.unstable","com.google.android.gms.chimera",
    "com.google.android.gms.auth","com.google.android.gms.location",
    "com.google.android.gms.cast.service","com.google.android.gms.backup",
    "com.google.android.gms.measurement","com.google.android.gms.ads",
    "com.google.android.gms.clearcut","com.google.android.gms.config",
    "com.google.android.gms.tapandpay","com.google.android.gms.wallet",
    "com.google.android.gms.security","com.google.android.gms.telephonyspam",
    "com.google.android.gms.update","com.google.android.gms.vision",
    "com.google.android.gms.wearable","com.google.android.gms.matchstick",
    "com.google.android.gms.deviceconnection","com.google.android.gms.droidguard",
    "com.google.android.gms.appinvite","com.google.android.gms.auth.api.phone",
    "com.google.android.instantapps.supervisor","com.google.android.webview",
    "com.google.android.networkstack","com.google.android.captiveportallogin",
    "com.google.android.documentsui","com.google.android.permissioncontroller",
    "com.google.android.packageinstaller","com.google.android.ext.shared",
    "com.android.vpndialogs","com.android.hotspot2","com.android.carrierdefaultapp",
    "com.android.storagemanager","com.android.shell","com.android.se",
    "com.android.traceur","com.android.wallpaperbackup","com.android.wallpapercropper",
    "com.android.providers.downloads.ui","com.android.providers.media.module",
    "com.android.providers.calendar","com.android.providers.userdictionary",
    "com.android.providers.blockednumber","com.android.certinstaller",
    "com.android.companiondevicemanager","com.android.htmlviewer",
    "com.android.inputdevices","com.android.keychain",
    "com.android.location.fused","com.android.managedprovisioning",
    "com.android.networkstack.inprocess","com.android.networkstack.tethering",
    "com.android.printspooler","com.android.proxyhandler",
    "com.android.server.telecom","com.android.simappdialog",
    "com.android.smspush","com.dsi.ant.server",
    "com.qualcomm.qti.qdma","com.qualcomm.qti.cne",
    "com.qualcomm.qti.telephonyservice","com.qualcomm.qti.ims",
    "org.codeaurora.ims","com.quicinc.cne.CNEService",
    "com.mediatek.ims","com.mediatek.telephony","com.mediatek.ygps",
    "com.sprd.engineermode","com.sprd.validationtools","com.unisoc.phone",
    "com.google.android.as","com.google.android.as.oss",
    "com.google.android.cellbroadcastreceiver","com.google.android.configupdater",
    "com.google.android.connectivity.healthlog","com.google.android.ims",
    "com.google.android.safetycore","com.google.android.tag",
    "com.google.mainline.telemetry",
    "com.google.android.overlay.gmsconfig",
    "com.google.android.overlay.modules.ext.services",
    "com.google.android.overlay.modules.modulemetadata",
    "com.google.android.tetheringentitlement",
    "com.google.android.printservice.recommendation",
    "com.qualcomm.qti.services.systemhelper","com.qualcomm.qti.callfeaturessetting",
    "com.mediatek.mtklogger","com.mediatek.providers.drm",
    "com.mediatek.security","com.mediatek.nlpservice",
    "com.samsung.android.incallui","com.samsung.android.kgclient",
    "com.samsung.android.sdm.config","com.samsung.android.server.telecom",
    "com.samsung.android.providers.contacts","com.samsung.android.providers.media",
    "com.xiaomi.xmsf","com.xiaomi.providers.applications",
    "com.xiaomi.providers.contacts","com.xiaomi.simactivate.service",
    "com.oppo.providers.media","com.oppo.providers.contacts",
    "com.coloros.providers.media","com.coloros.providers.contacts",
    "com.transsion.providers.media","com.transsion.providers.contacts",
    "com.megvii.faceassistant","com.fingerprints.service",
    "com.goodix.fingerprint","com.arcsoft.arcfuseloader",
    "com.dolby.daxservice","com.dolby.ds1appUI",
    "com.realtek.hardware","com.immersion.haptics",
    "com.nxp.nfc","com.broadcom.nfc","com.marvell.nfc",
    "com.sonyericsson.extras","com.samsung.android.svoiceime",
    "com.samsung.tmovvm","com.sec.android.app.magnifier",
    "com.sec.android.app.parser","com.sec.android.soagent",
    "com.sec.android.widgetapp.samsungapps",
    "com.samsung.android.allshare.service.mediashare",
    "com.samsung.android.app.ledcoverdream","com.samsung.android.authfw",
    "com.samsung.android.da.daagent","com.samsung.android.drivelink",
    "com.samsung.android.email.provider","com.samsung.android.hmt.drvs",
    "com.samsung.android.mdm","com.samsung.android.spdf",
    "com.xiaomi.account","com.xiaomi.payment",
    "com.xiaomi.smarthome","com.xiaomi.hm.health",
    "com.oppo.push","com.heytap.mcsservice","com.heytap.openid",
    "com.coloros.assistant","com.transsion.payment",
]

# ── Common user apps (package, weight) ──
COMMON_USER_APPS = [
    ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20),("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",10),("com.instagram.android","com.instagram.android.MainTabActivity",5),
    ("com.facebook.katana","com.facebook.katana.LoginActivity",4),("com.facebook.lite","com.facebook.lite.MainActivity",4),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",4),
    ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3),("com.twitter.android","com.twitter.android.MainActivity",2),("com.spotify.music","com.spotify.music.MainActivity",2),
    ("com.netflix.mediaclient","com.netflix.mediaclient.ui.launch.UIWebViewActivity",1.5),("com.google.android.apps.youtube.music","com.google.android.apps.youtube.music.HomeActivity",1.5),
    ("com.zhiliaoapp.musically.go","com.zhiliaoapp.musically.go.SplashActivity",2),("com.kwai.video","com.kwai.video.SplashActivity",1),("com.pinterest","com.pinterest.activity.PinterestActivity",1),
    ("com.linkedin.android","com.linkedin.android.authenticator.LaunchActivity",1),("com.reddit.frontpage","com.reddit.frontpage.SplashActivity",1),("com.quora.android","com.quora.android.SplashActivity",0.5),
    ("id.dana","id.dana.MainActivity",3),("com.gojek.app","com.gojek.app.SplashActivity",3),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",3),
    ("com.tokopedia.tkpd","com.tokopedia.tkpd.activity.SplashScreenActivity",2),("com.grab.id","com.grab.id.SplashActivity",2),("com.bukalapak.android","com.bukalapak.android.SplashActivity",1),
    ("id.co.bca","id.co.bca.mobile.banking.MainActivity",2),("id.co.bni","id.co.bni.mobile.MainActivity",1.5),("id.co.bri","id.co.bri.mobile.MainActivity",1.5),
    ("id.co.bankbkemobile.digitalbank","id.co.bankbkemobile.digitalbank.MainActivity",1),("com.telkom.mwallet","com.telkom.mwallet.MainActivity",1),
    ("com.binance.dev","com.binance.dev.SplashActivity",2),("com.coinbase.android","com.coinbase.android.SplashActivity",1),("com.okx.wallet","com.okx.wallet.SplashActivity",1),
    ("com.android.chrome","com.google.android.apps.chrome.Main",3),("org.mozilla.firefox","org.mozilla.firefox.MainActivity",1),("com.opera.browser","com.opera.browser.MainActivity",1),
    ("com.microsoft.teams","com.microsoft.teams.ui.SplashActivity",1.5),("com.microsoft.office.outlook","com.microsoft.office.outlook.MainActivity",1),
    ("com.google.android.apps.docs","com.google.android.apps.docs.app.NewMainProxyActivity",1.5),("com.google.android.apps.maps","com.google.android.maps.MapsActivity",2),
    ("cn.wps.moffice_eng","cn.wps.moffice_eng.MainActivity",1),("com.adobe.reader","com.adobe.reader.MainActivity",0.5),
    ("com.duolingo","com.duolingo.SplashActivity",1),("com.shazam.android","com.shazam.android.MainActivity",0.5),("com.canva.editor","com.canva.editor.SplashActivity",1),
    ("com.picsart.studio","com.picsart.studio.SplashActivity",1),("com.ubercab","com.ubercab.MainActivity",1),("com.airbnb.android","com.airbnb.android.MainActivity",0.5),
    ("com.booking","com.booking.MainActivity",0.5),("com.traveloka.android","com.traveloka.android.SplashActivity",1),
    ("com.mobile.legends","com.mobile.legends.SplashActivity",2),("com.garena.game.codm","com.garena.game.codm.SplashActivity",1.5),
    ("com.supercell.clashofclans","com.supercell.clashofclans.GameApp",1),("com.pubg.mobile","com.pubg.mobile.SplashActivity",1.5),
    ("com.dts.freefiremax","com.dts.freefiremax.SplashActivity",1),("com.joox","com.joox.MainActivity",1),("com.deezer.android.app","com.deezer.android.app.MainActivity",0.5),
    ("tv.twitch.android.app","tv.twitch.android.app.MainActivity",1),("com.discord","com.discord.main.MainActivity",1),
    ("com.snapchat.android","com.snapchat.android.LandingPageActivity",1.5),("com.viber.voip","com.viber.voip.MainActivity",0.5),
    ("com.skype.raider","com.skype.raider.MainActivity",0.5),("us.zoom.videomeetings","us.zoom.videomeetings.MainActivity",1),
    ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",1),("com.anthropic.claude","com.anthropic.claude.MainActivity",0.5),
    ("com.ebay.mobile","com.ebay.mobile.MainActivity",0.5),("com.amazon.mShop.android.shopping","com.amazon.mShop.android.shopping.MainActivity",0.5),
    ("com.aliexpress","com.aliexpress.MainActivity",1),("com.lazada.android","com.lazada.android.MainActivity",1),
    ("com.pou.app","com.pou.app.MainActivity",0.5),("com.king.candycrushsaga","com.king.candycrushsaga.MainActivity",0.5),
    ("com.imdb.mobile","com.imdb.mobile.MainActivity",0.3),("com.medium.reader","com.medium.reader.SplashActivity",0.3),
    ("com.nytimes.android","com.nytimes.android.SplashActivity",0.3),("com.bbc.news","com.bbc.news.SplashActivity",0.3),
    ("com.detik.android","com.detik.android.SplashActivity",0.3),("id.co.kompas","id.co.kompas.SplashActivity",0.3),
]

# ── Brand profiles ──
BP: Dict[str, Any] = {
    "samsung": {
        "models": ["samsung SM-A057F","samsung SM-A155F","samsung SM-A226B","samsung SM-A035F","samsung SM-A105G","samsung SM-A325F","samsung SM-G990B"],
        "av": ["11","12","13","14"], "ec": [20000, 90000], "cp": [0.62, 0.84],
        "system": SAMSUNG_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20.5),("com.sec.android.app.launcher","com.sec.android.app.launcher.Launcher",15),("android","android.app.Activity",5.8),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.4),("com.instagram.android","com.instagram.android.MainTabActivity",4.3),
            ("com.facebook.katana","com.facebook.katana.LoginActivity",3.8),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.7),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3.5),("com.android.chrome","com.google.android.apps.chrome.Main",3.4),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",3.0),("com.samsung.android.dialer","com.samsung.android.dialer.DialtactsActivity",2.4),
            ("com.samsung.android.messaging","com.samsung.android.messaging.ui.ConversationListActivity",2.2),("com.sec.android.gallery3d","com.sec.android.gallery3d.app.Gallery",2.1),
            ("com.sec.android.app.camera","com.sec.android.app.camera.Camera",1.8),("com.android.settings","com.android.settings.Settings",1.8),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),("id.dana","id.dana.MainActivity",1.4),("com.gojek.app","com.gojek.app.SplashActivity",1.4),
            ("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.3),("com.tokopedia.tkpd","com.tokopedia.tkpd.activity.SplashScreenActivity",1.2),
            ("com.spotify.music","com.spotify.music.MainActivity",1.1),("com.android.vending","com.android.vending.AssetBrowserActivity",1.1),
            ("com.samsung.android.calendar","com.samsung.android.calendar.LaunchActivity",0.8),("com.samsung.android.bixby.agent","com.samsung.android.bixby.agent.SplashActivity",0.7),
            ("com.samsung.android.spay","com.samsung.android.spay.SplashActivity",0.5),("com.samsung.android.themestore","com.samsung.android.themestore.SplashActivity",0.4),
            ("com.samsung.android.game.gamehome","com.samsung.android.game.gamehome.SplashActivity",0.3),("com.microsoft.teams","com.microsoft.teams.ui.SplashActivity",0.3),
            ("com.netflix.mediaclient","com.netflix.mediaclient.ui.launch.UIWebViewActivity",0.3),("com.binance.dev","com.binance.dev.SplashActivity",0.2),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.2),
        ],
    },
    "xiaomi": {
        "models": ["Xiaomi 2201117PG","Xiaomi M2006C3MG","Xiaomi M2010J19SG","Xiaomi 24075RP89G","Redmi Note 13","Xiaomi 23053RN02A","Xiaomi M2007J20CG"],
        "av": ["11","12","13","14"], "ec": [25000, 110000], "cp": [0.58, 0.80],
        "system": XIAOMI_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",17),("com.miui.home","com.miui.home.launcher.Launcher",12),("com.mi.android.globallauncher","com.mi.android.globallauncher.Launcher",7.2),
            ("android","android.app.Activity",5.8),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.8),("com.android.chrome","com.google.android.apps.chrome.Main",4.4),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.0),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.4),("com.google.android.youtube","com.google.android.youtube.HomeActivity",3.2),
            ("com.xiaomi.mipicks","com.xiaomi.mipicks.SplashActivity",2.6),("com.miui.securitycenter","com.miui.securitycenter.MainActivity",2.4),
            ("com.miui.gallery","com.miui.gallery.activity.HomePageActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.google.android.apps.photos","com.google.android.apps.photos.home.HomeActivity",1.8),("id.dana","id.dana.MainActivity",1.6),
            ("com.gojek.app","com.gojek.app.SplashActivity",1.5),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.4),
            ("com.mobile.legends","com.mobile.legends.SplashActivity",1.3),("com.android.vending","com.android.vending.AssetBrowserActivity",1.2),
            ("com.miui.weather2","com.miui.weather2.ActivityWeatherMain",1.0),("com.miui.notes","com.miui.notes.ui.NotesListActivity",0.8),
            ("com.xiaomi.scanner","com.xiaomi.scanner.SplashActivity",0.5),("com.xiaomi.shop","com.xiaomi.shop.SplashActivity",0.4),
            ("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",0.3),("com.facebook.lite","com.facebook.lite.MainActivity",0.3),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.2),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.2),
        ],
    },
    "oppo": {
        "models": ["OPPO CPH2577","OPPO CPH2387","OPPO CPH1909","OPPO CPH2591","OPPO CPH2059"],
        "av": ["11","12","13","14"], "ec": [20000, 85000], "cp": [0.60, 0.84],
        "system": OPPO_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",16.5),("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",10),("com.oppo.launcher","com.oppo.launcher.Launcher",14),
            ("android","android.app.Activity",6.0),("com.facebook.lite","com.facebook.lite.MainActivity",5.5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.5),
            ("com.android.chrome","com.google.android.apps.chrome.Main",4.0),("com.coloros.recents","com.coloros.recents.RecentsActivity",3.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.4),("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3.0),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.6),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.4),
            ("com.android.settings","com.android.settings.Settings",2.2),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.9),
            ("id.dana","id.dana.MainActivity",1.6),("com.gojek.app","com.gojek.app.SplashActivity",1.5),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.4),
            ("com.spotify.music","com.spotify.music.MainActivity",1.2),("com.android.vending","com.android.vending.AssetBrowserActivity",1.2),
            ("com.oppo.camera","com.oppo.camera.CameraActivity",1.0),("com.coloros.gallery3d","com.coloros.gallery3d.app.Gallery",0.8),
            ("com.binance.dev","com.binance.dev.SplashActivity",0.3),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.2),
        ],
    },
    "infinix": {
        "models": ["Infinix X6833B","Infinix X669C","Infinix X6728B","Infinix X6886"],
        "av": ["12","13","14"], "ec": [25000, 70000], "cp": [0.62, 0.83],
        "system": INFINIX_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",17),("com.transsion.hilauncher","com.transsion.hilauncher.Launcher",13),("android","android.app.Activity",5.5),
            ("tw.nekomimi.nekogram","tw.nekomimi.nekogram.SplashActivity",6),("com.android.chrome","com.google.android.apps.chrome.Main",4.5),
            ("com.instagram.android","com.instagram.android.MainTabActivity",4.0),("com.twitter.android","com.twitter.android.MainActivity",3.5),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3.2),("com.authy.authy","com.authy.authy.SplashActivity",3.0),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",2.8),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",2.5),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("id.dana","id.dana.MainActivity",1.6),("com.gojek.app","com.gojek.app.SplashActivity",1.5),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",1.4),
            ("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.2),("com.android.vending","com.android.vending.AssetBrowserActivity",1.1),
            ("com.binance.dev","com.binance.dev.SplashActivity",1.0),("com.google.android.youtube","com.google.android.youtube.HomeActivity",1.0),
        ],
    },
    "vivo": {
        "models": ["vivo V2322","vivo V2134","vivo V2227","vivo V2058"],
        "av": ["12","13","14","15"], "ec": [25000, 90000], "cp": [0.60, 0.82],
        "system": [],
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20),("com.android.launcher3","com.android.launcher3.Launcher",12),("android","android.app.Activity",4.5),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",5),("com.whatsapp.w4b","com.whatsapp.w4b.MainWhatsAppActivity",3.5),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",3.2),("com.android.chrome","com.google.android.apps.chrome.Main",3.0),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",2.8),("com.instagram.android","com.instagram.android.MainTabActivity",2.5),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.facebook.lite","com.facebook.lite.MainActivity",1.8),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.5),
            ("id.dana","id.dana.MainActivity",1.4),("com.gojek.app","com.gojek.app.SplashActivity",1.3),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.2),
            ("com.binance.dev","com.binance.dev.SplashActivity",1.0),("com.spotify.music","com.spotify.music.MainActivity",0.8),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",0.8),("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.5),
        ],
    },
    "realme": {
        "models": ["realme RMX3263","realme RMX5388","realme RMX1821","realme RMX3085"],
        "av": ["10","11","12","13","14","15"], "ec": [20000, 95000], "cp": [0.60, 0.83],
        "system": OPPO_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",20),("com.android.launcher3","com.android.launcher3.Launcher",12),("android","android.app.Activity",5.5),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",4.0),("com.instagram.android","com.instagram.android.MainTabActivity",3.5),
            ("com.facebook.katana","com.facebook.katana.LoginActivity",3.0),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",3.0),
            ("org.telegram.messenger","org.telegram.messenger.DefaultIcon",2.8),("com.android.chrome","com.google.android.apps.chrome.Main",2.5),
            ("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.2),("com.android.settings","com.android.settings.Settings",2.0),
            ("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.8),("id.dana","id.dana.MainActivity",1.5),
            ("com.gojek.app","com.gojek.app.SplashActivity",1.4),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.3),
            ("com.google.android.apps.photos","com.google.android.apps.photos.home.HomeActivity",1.0),("com.spotify.music","com.spotify.music.MainActivity",0.8),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",0.8),("com.binance.dev","com.binance.dev.SplashActivity",0.4),
            ("com.openai.chatgpt","com.openai.chatgpt.MainActivity",0.3),
        ],
    },
    "advan": {
        "models": ["Advan G5","Advan G9 Pro","Advan i6C"],
        "av": ["11","12","13"], "ec": [15000,60000], "cp": [0.56,0.78],
        "system": [],
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",18),("com.advan.launcher","com.advan.launcher.Launcher",11),("android","android.app.Activity",6),
            ("com.android.chrome","com.google.android.apps.chrome.Main",5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.2),
            ("com.instagram.android","com.instagram.android.MainTabActivity",3.6),("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",3),
            ("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.8),("com.google.android.youtube","com.google.android.youtube.HomeActivity",2.4),
            ("com.android.settings","com.android.settings.Settings",2.2),("id.dana","id.dana.MainActivity",1.8),("com.gojek.app","com.gojek.app.SplashActivity",1.6),
            ("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.4),("com.google.android.gm","com.google.android.gm.ConversationListActivityGmail",1.2),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",1.1),("com.spotify.music","com.spotify.music.MainActivity",1),
            ("com.facebook.katana","com.facebook.katana.LoginActivity",1),
        ],
    },
    "tecno": {
        "models": ["TECNO TECNO LI7","TECNO TECNO AD8","TECNO TECNO BF7","TECNO SPARK 10"],
        "av": ["12","13","14","15"], "ec": [20000,75000], "cp": [0.60,0.82],
        "system": INFINIX_SYSTEM,
        "apps": [
            ("com.whatsapp","com.whatsapp.MainWhatsAppActivity",17),("com.transsion.hilauncher","com.transsion.hilauncher.Launcher",13),("android","android.app.Activity",5.5),
            ("com.kubi.kucoin","com.kubi.kucoin.SplashActivity",5),("org.telegram.messenger","org.telegram.messenger.DefaultIcon",4.5),
            ("com.transsion.microintelligence","com.transsion.microintelligence.SplashActivity",3),("com.android.chrome","com.google.android.apps.chrome.Main",2.8),
            ("com.instagram.android","com.instagram.android.MainTabActivity",2.5),("com.ss.android.ugc.trill","com.ss.android.ugc.trill.MainActivity",2.2),
            ("com.google.android.gms","com.google.android.gms.GOOGLE_PLAY_SERVICES",2),("com.android.settings","com.android.settings.Settings",1.8),
            ("id.dana","id.dana.MainActivity",1.5),("com.gojek.app","com.gojek.app.SplashActivity",1.4),("com.shopee.id","com.shopee.id.ui.activity.HomeActivity",1.3),
            ("com.binance.dev","com.binance.dev.SplashActivity",1.2),("com.google.android.youtube","com.google.android.youtube.HomeActivity",1),
            ("com.android.vending","com.android.vending.AssetBrowserActivity",0.8),("com.facebook.lite","com.facebook.lite.MainActivity",0.5),
        ],
    },
}


# ══════════════════════════════════════════
#  GENERATOR ENGINE
# ══════════════════════════════════════════

def _norm_apps(items):
    """Normalize app list to (package, class, weight) tuples."""
    if items and len(items[0]) == 2:
        s = sum(w for _, w in items)
        return [(p, "", w / s) for p, w in items]
    s = sum(w for _, _, w in items)
    return [(p, c, w / s) for p, c, w in items]


def _build_pool(brand, prof, rng):
    """Build realistic package pool with 300+ unique packages."""
    apps = _norm_apps(prof["apps"])
    brand_sys = prof.get("system", [])

    # Pick random system apps (60-90% of available)
    sys_pick = [p for p in SYSTEM_APPS + brand_sys if rng.random() < rng.uniform(0.85, 0.99)]
    # Pick random bg services (40-70%)
    bg_pick = [p for p in BG_SERVICES if rng.random() < rng.uniform(0.8, 0.98)]

    # Extra user apps (30-60%)
    extra_raw = [(item[0], item[-1]) for item in COMMON_USER_APPS if rng.random() < rng.uniform(0.6, 0.9)]
    extra = _norm_apps(extra_raw)

    # Combine main + extra (reduced weight)
    all_apps = list(apps)
    for p, _, w in extra:
        all_apps.append((p, "", w * 0.15))

    total_w = sum(w for _, _, w in all_apps)
    all_apps = [(p, c, w / total_w) for p, c, w in all_apps]
    return all_apps, sys_pick, bg_pick


def _gen(brand, model, av, count, seed, days):
    rng = random.Random(seed)
    prof = BP[brand]
    model = model or rng.choice(prof["models"])
    av = av or rng.choice(prof["av"])
    if count is None:
        lo, hi = prof["ec"]
        count = rng.randint(lo, hi)
    count = min(count, 120000)
    if days is None:
        days = rng.uniform(7.1, 9.8)

    # Time window
    end = dt.datetime(2026, 5, 28, rng.randint(5, 20), rng.randint(0, 59), rng.randint(0, 59), tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days, minutes=rng.randint(0, 180), seconds=rng.randint(0, 59))

    # Build package pool
    apps, sys_pkgs, bg_pkgs = _build_pool(brand, prof, rng)
    pkgs = [p for p, _, _ in apps]
    cls = {p: c for p, c, _ in apps}
    pw = [w for _, _, w in apps]

    ct = rng.uniform(*prof["cp"])
    tn = [t for t, _ in EW]
    tw = [w * rng.uniform(0.82, 1.18) for _, w in EW]

    # Hour weights with randomness
    bh = [w * rng.uniform(0.85, 1.15) for w in BH_INDONESIA]
    bh_sum = sum(bh)
    bh = [w / bh_sum for w in bh]

    # Day allocation
    ds = []
    d = start.date()
    while d <= end.date():
        ds.append(d)
        d += dt.timedelta(days=1)

    ws = []
    for day in ds:
        w = 1.0
        if day.weekday() in (5, 6):
            w *= rng.uniform(1.05, 1.35)
        if day.weekday() == 0:
            w *= rng.uniform(0.72, 1.05)
        if day == start.date():
            w *= rng.uniform(0.32, 0.65)
        if day == end.date():
            w *= rng.uniform(0.35, 0.75)
        w *= rng.uniform(0.68, 1.42)
        ws.append(w)

    s = sum(ws)
    dc = {d: int(round(count * w / s)) for d, w in zip(ds, ws)}
    while sum(dc.values()) < count:
        dc[rng.choice(ds)] += 1
    while sum(dc.values()) > count:
        k = rng.choice([d for d in ds if dc[d] > 20])
        dc[k] -= 1

    rows = []

    for day, nd in sorted(dc.items()):
        hw = [max(0.0004, w * rng.uniform(0.7, 1.35)) for w in bh]
        if day.weekday() in (5, 6):
            for h in range(10, 23):
                hw[h] *= rng.uniform(1.02, 1.32)
        hs = sum(hw)
        hw = [x / hs for x in hw]

        # Session-based generation: each session = one package, multiple events
        # Session size distribution: fat-tailed (most are small, some are huge)
        day_events = 0
        while day_events < int(nd * 0.95):
            # Pick a random hour weighted by distribution
            hr = rng.choices(range(24), weights=hw, k=1)[0]

            # Session size: fat-tailed distribution
            r = rng.random()
            if r < 0.60:
                session_size = rng.randint(1, 8)
            elif r < 0.85:
                session_size = rng.randint(8, 40)
            elif r < 0.95:
                session_size = rng.randint(40, 150)
            elif r < 0.99:
                session_size = rng.randint(150, 300)
            else:
                session_size = rng.randint(300, 450)

            session_size = min(session_size, nd - day_events)
            if session_size <= 0:
                break

            # Pick session package
            sp = rng.choices(pkgs, weights=pw, k=1)[0]
            # Sometimes use system/bg package for the session
            if rng.random() < 0.15 and sys_pkgs:
                sp = rng.choice(sys_pkgs)
            elif rng.random() < 0.05 and bg_pkgs:
                sp = rng.choice(bg_pkgs)

            # Session start time
            cur = dt.datetime(day.year, day.month, day.day, hr,
                              rng.randrange(60), rng.randrange(60),
                              rng.randrange(1000) * 1000, tzinfo=dt.timezone.utc)
            if cur < start:
                cur = start + dt.timedelta(seconds=rng.randint(0, 2400))
            if cur > end:
                cur = end - dt.timedelta(seconds=rng.randint(0, 2400))

            # Generate events in this session
            for i in range(session_size):
                if i:
                    # Inter-event gap (mostly small for bursts)
                    r = rng.random()
                    if r < 0.12:
                        delta = 0  # concurrent event (same timestamp)
                    elif r < 0.50:
                        delta = rng.uniform(0.02, 0.8)
                    elif r < 0.72:
                        delta = rng.uniform(1, 10)
                    elif r < 0.88:
                        delta = rng.uniform(10, 60)
                    elif r < 0.96:
                        delta = rng.uniform(60, 600)
                    else:
                        delta = rng.uniform(600, 2400)
                    cur += dt.timedelta(seconds=delta, milliseconds=rng.randint(0, 25))

                if not (start <= cur <= end):
                    continue

                # Package: mostly session package, sometimes switch
                pp = sp
                if rng.random() < 0.20:
                    # Switch to a different package temporarily
                    pp = rng.choices(pkgs, weights=pw, k=1)[0]
                elif rng.random() < 0.05 and sys_pkgs:
                    pp = rng.choice(sys_pkgs)
                elif rng.random() < 0.02 and bg_pkgs:
                    pp = rng.choice(bg_pkgs)
                # Hard cap: force switch if same package streak > 160
                if rows and pp == rows[-1]["package"]:
                    same_streak = 1
                    for prev in reversed(rows):
                        if prev["package"] == pp:
                            same_streak += 1
                        else:
                            break
                    if same_streak >= 160:
                        pp = rng.choices(pkgs, weights=pw, k=1)[0]

                # Event type
                if i == 0 and rng.random() < 0.7:
                    typ = "ACTIVITY_RESUMED"
                elif i == session_size - 1 and rng.random() < 0.63:
                    typ = "ACTIVITY_PAUSED"
                else:
                    typ = rng.choices(tn, weights=tw, k=1)[0]

                rec = {"ts": int(cur.timestamp() * 1000) + rng.randint(0, 12), "package": pp, "type": typ}

                # Class field
                c = cls.get(pp, "")
                if c:
                    if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION", "CONFIGURATION_CHANGE"):
                        h = rng.random() < min(0.96, ct + 0.22)
                    elif typ.startswith("FOREGROUND_SERVICE"):
                        h = rng.random() < max(0.25, ct - 0.3)
                    elif typ.startswith("SCREEN") or typ.startswith("KEYGUARD") or typ == "STANDBY_BUCKET_CHANGED":
                        h = rng.random() < max(0.04, ct - 0.58)
                    else:
                        h = rng.random() < max(0.08, ct - 0.48)
                    if h:
                        rec["class"] = c
                elif rng.random() < 0.40 and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23", "USER_INTERACTION"):
                    rec["class"] = pp + ".MainActivity"

                rows.append(rec)

            day_events += session_size

    rows.sort(key=lambda r: r["ts"])

    # Post-process: inject mega-bursts, long streaks, extra unique packages
    rows = _post_process(rows, start, end, pkgs, pw, sys_pkgs, bg_pkgs, cls, tn, tw, ct, rng, count)
    rows.sort(key=lambda r: r["ts"])

    # Trim to count — preserve post-processing bursts by trimming from padding events first
    if len(rows) > count:
        # Sort by timestamp, remove events from the end (padding) first
        rows.sort(key=lambda r: r["ts"])
        rows = rows[:count]
    while len(rows) < count:
        cur = start + dt.timedelta(seconds=rng.randint(0, max(1, int((end - start).total_seconds()))),
                                   milliseconds=rng.randint(0, 999))
        pp = rng.choices(pkgs, weights=pw, k=1)[0]
        typ = rng.choices(tn, weights=tw, k=1)[0]
        rec = {"ts": int(cur.timestamp() * 1000), "package": pp, "type": typ}
        if typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23") and rng.random() < 0.86 and cls.get(pp):
            rec["class"] = cls[pp]
        elif rng.random() < 0.40 and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23"):
            rec["class"] = pp + ".MainActivity"
        rows.append(rec)

    rows.sort(key=lambda r: r["ts"])

    # Cap same-package streaks at 160 — break long runs with package switches
    MAX_STREAK = 160
    i = 0
    while i < len(rows):
        j = i + 1
        while j < len(rows) and rows[j]["package"] == rows[i]["package"]:
            j += 1
        run_len = j - i
        if run_len > MAX_STREAK:
            # Break every MAX_STREAK events by switching package
            for k in range(i + MAX_STREAK, j, MAX_STREAK):
                alt = rng.choices(pkgs, weights=pw, k=1)[0]
                if alt == rows[k]["package"]:
                    for p in (sys_pkgs + bg_pkgs + pkgs):
                        if p != rows[k]["package"]:
                            alt = p
                            break
                rows[k]["package"] = alt
        i = j
    rows.sort(key=lambda r: r["ts"])

    mn = dt.datetime.fromtimestamp(rows[0]["ts"] / 1000, dt.timezone.utc)
    mx = dt.datetime.fromtimestamp(rows[-1]["ts"] / 1000, dt.timezone.utc)
    iso = lambda t: t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "schema_version": 1, "app_version": "1.0.0",
        "android_version": av, "device_model": model,
        "export_generated_at": iso(mx),
        "window_start": iso(mn), "window_end": iso(mx),
        "event_count": len(rows),
        "notes": "Event-level data subject to Android system retention; older periods may be summarised only."
    }
    return rows, manifest



def _post_process(rows, start, end, pkgs, pw, sys_pkgs, bg_pkgs, cls, tn, tw, ct, rng, count):
    """Inject mega-bursts, long streaks, and extra unique packages."""
    
    # 1. Inject 2-4 mega-bursts (400-600 events, same package, <1s gaps)
    for _ in range(2):
        burst_size = rng.randint(410, 520)
        # Pick a random time in the window
        base_ts = start.timestamp() + rng.random() * (end.timestamp() - start.timestamp())
        burst_pkg = rng.choices(pkgs, weights=pw, k=1)[0]
        # Use 2-3 packages in mega-burst to keep burst max high but same-pkg max low
        burst_pkgs = [burst_pkg]
        if rng.random() < 0.7:
            burst_pkgs.append(rng.choices(pkgs, weights=pw, k=1)[0])
        if rng.random() < 0.3:
            burst_pkgs.append(rng.choices(pkgs, weights=pw, k=1)[0])
        
        cur_ts = base_ts
        for i in range(burst_size):
            if i:
                cur_ts += rng.uniform(0.02, 0.95)  # <1s gap
            
            cur_dt = dt.datetime.fromtimestamp(cur_ts, dt.timezone.utc)
            if not (start <= cur_dt <= end):
                continue
            
            typ = rng.choices(tn, weights=tw, k=1)[0]
            if i == 0:
                typ = "ACTIVITY_RESUMED"
            elif i == burst_size - 1:
                typ = "ACTIVITY_PAUSED"
            
            rec = {"ts": int(cur_ts * 1000) + rng.randint(0, 12), "package": rng.choice(burst_pkgs), "type": typ}
            c = cls.get(rec["package"], "")
            if c and rng.random() < 0.80:
                rec["class"] = c
            rows.append(rec)
    
    # 2. Inject 5-10 long same-package streaks (80-155 events)
    prev_streak_pkg = ""
    for _ in range(4):
        streak_size = rng.randint(85, 135)
        base_ts = start.timestamp() + rng.random() * (end.timestamp() - start.timestamp())
        streak_pkg = rng.choices(pkgs[:8], weights=pw[:8], k=1)[0]  # top 8 packages
        # Ensure different package from previous streaks
        if streak_pkg == prev_streak_pkg:
            streak_pkg = rng.choices(pkgs[2:8], weights=pw[2:8], k=1)[0]
        prev_streak_pkg = streak_pkg
        
        cur_ts = base_ts
        for i in range(streak_size):
            if i:
                # Mix of small and medium gaps
                r = rng.random()
                if r < 0.70:
                    cur_ts += rng.uniform(0.5, 5.0)
                elif r < 0.90:
                    cur_ts += rng.uniform(5, 30)
                else:
                    cur_ts += rng.uniform(30, 120)
            
            cur_dt = dt.datetime.fromtimestamp(cur_ts, dt.timezone.utc)
            if not (start <= cur_dt <= end):
                continue
            
            typ = rng.choices(tn, weights=tw, k=1)[0]
            rec = {"ts": int(cur_ts * 1000) + rng.randint(0, 12), "package": streak_pkg, "type": typ}
            c = cls.get(streak_pkg, "")
            if c and rng.random() < 0.80:
                rec["class"] = c
            rows.append(rec)
    
    # 3. Inject extra unique package events to boost unique count
    # Add events for system/bg packages that aren't yet in the dataset
    existing_pkgs = set(r["package"] for r in rows)
    missing_sys = [p for p in sys_pkgs if p not in existing_pkgs]
    missing_bg = [p for p in bg_pkgs if p not in existing_pkgs]
    
    # Inject ALL missing packages — spread across timeline to survive trimming
    extra_pkgs = missing_sys + missing_bg
    rng.shuffle(extra_pkgs)
    total_span = (end - start).total_seconds()
    for idx, pkg in enumerate(extra_pkgs):
        # Spread evenly across timeline + small random offset
        frac = (idx + 0.5) / max(len(extra_pkgs), 1)
        base_ts = start.timestamp() + frac * total_span + rng.uniform(-1800, 1800)
        cur_dt = dt.datetime.fromtimestamp(base_ts, dt.timezone.utc)
        if not (start <= cur_dt <= end):
            base_ts = start.timestamp() + rng.random() * total_span
        typ = rng.choices(tn, weights=tw, k=1)[0]
        rec = {"ts": int(base_ts * 1000) + rng.randint(0, 12), "package": pkg, "type": typ}
        if rng.random() < 0.35 and typ in ("ACTIVITY_RESUMED", "ACTIVITY_PAUSED", "EVENT_23"):
            rec["class"] = pkg + ".MainActivity"
        rows.append(rec)
    
    return rows

def _analyze(rows):
    pkg = collections.Counter(r["package"] for r in rows)
    typ = collections.Counter(r["type"] for r in rows)
    gaps = [(b["ts"] - a["ts"]) / 1000 for a, b in zip(rows, rows[1:])]
    cp = sum(1 for r in rows if "class" in r) / len(rows) * 100 if rows else 0

    def q(vs, n):
        if not vs:
            return 0
        vs = sorted(vs)
        return vs[min(len(vs) - 1, int((len(vs) - 1) * n))]

    def H(c):
        t = sum(c.values())
        return -sum((v / t) * math.log2(v / t) for v in c.values() if v and t) if t else 0

    return {
        "event_count": len(rows), "unique_packages": len(pkg),
        "package_entropy": round(H(pkg), 3), "event_type_entropy": round(H(typ), 3),
        "class_presence_pct": round(cp, 2),
        "gap_p50": round(q(gaps, 0.5), 3), "gap_p90": round(q(gaps, 0.9), 3),
        "gap_p99": round(q(gaps, 0.99), 3),
        "lte1": round(sum(g <= 1 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "gt10m": round(sum(g > 600 for g in gaps) / len(gaps) * 100, 2) if gaps else 0,
        "top_packages": pkg.most_common(30), "event_types": typ.most_common()
    }


def _score(m):
    s = 100
    if not (5000 <= m["event_count"] <= 120000):
        s -= 15
    if not (44 <= m["class_presence_pct"] <= 86):
        s -= 18
    if not (0.25 <= m["gap_p50"] <= 1.2):
        s -= 18
    if not (8 <= m["gap_p90"] <= 60):
        s -= 12
    if not (50 <= m["gap_p99"] <= 950):
        s -= 8
    if not (48 <= m["lte1"] <= 80):
        s -= 14
    if not (0.05 <= m["gt10m"] <= 3):
        s -= 8
    if not (2.5 <= m["package_entropy"] <= 6.8):
        s -= 6
    if not (1.2 <= m["event_type_entropy"] <= 3.8):
        s -= 6
    return max(0, s)


def _zip(rows, manifest):
    nd = "\n".join(json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in rows) + "\n"
    ms = json.dumps(manifest, separators=(",", ":"), ensure_ascii=False)
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("events.ndjson", nd)
        z.writestr("manifest.json", ms)
    d = buf.getvalue()
    return d, hashlib.sha256(d).hexdigest()


# ══════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def index():
    import pathlib
    # Try multiple paths for Vercel / local compatibility
    for p in [
        pathlib.Path(__file__).resolve().parent.parent / "index.html",
        pathlib.Path("/var/task/index.html"),
        pathlib.Path("index.html"),
    ]:
        if p.exists():
            return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse(
        "<html><body><h1>SW Events Generator</h1>"
        "<p>index.html not found. Place it in project root.</p></body></html>"
    )


@app.get("/api/profiles")
def profiles():
    return {b: {"models": p["models"], "android_versions": p["av"],
                 "event_count_range": p["ec"]}
            for b, p in BP.items()}


@app.post("/api/generate")
def generate(brand: str = Form("xiaomi"), model: Optional[str] = Form(None),
             android: Optional[str] = Form(None), count: Optional[str] = Form(None),
             days: Optional[str] = Form(None), seed: Optional[str] = Form(None)):
    brand = brand.lower().strip()
    if brand not in BP:
        raise HTTPException(400, "Unknown brand")

    def pi(v, lo, hi):
        if not v or not v.strip():
            return None
        n = int(v.strip())
        if not lo <= n <= hi:
            raise HTTPException(400, f"Must be {lo}-{hi}")
        return n

    def pf(v, lo, hi):
        if not v or not v.strip():
            return None
        n = float(v.strip())
        if not lo <= n <= hi:
            raise HTTPException(400, f"Must be {lo}-{hi}")
        return n

    try:
        rows, manifest = _gen(
            brand, (model or "").strip() or None, (android or "").strip() or None,
            pi(count, 1000, 120000), pi(seed, 0, 999999999), pf(days, 1, 14)
        )
    except Exception as e:
        raise HTTPException(500, str(e))

    m = _analyze(rows)
    sc = _score(m)
    zb, sha = _zip(rows, manifest)
    return {
        "filename": "sw_events", "zip_size": len(zb), "zip_sha256": sha,
        "zip_base64": base64.b64encode(zb).decode(),
        "summary": {
            "device_model": manifest["device_model"],
            "android_version": manifest["android_version"],
            "event_count": manifest["event_count"],
            "window_start": manifest["window_start"],
            "window_end": manifest["window_end"],
            "score": sc, "sha256": sha, "zip_size": len(zb),
            "top_packages": m["top_packages"][:10],
            "event_types": m["event_types"][:10],
            "unique_packages": m["unique_packages"],
        },
        "notice": "Synthetic QA fixture only."
    }
