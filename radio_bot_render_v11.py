import asyncio
import random
import sys
import json
import os
from highrise import BaseBot, User, Position, RoomPermissions, AnchorPosition, Item, CurrencyItem
from highrise.models import SessionMetadata
from highrise.__main__ import main, BotDefinition

# Resolve encoding issues on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.owners = ["omar___p", "EZ11", "BM15", "N97_"]  # 👑 الملاك
        self.admins = ["", ""]  # قائمة المشرفين
        self.vip_users = []  # ⭐ قائمة VIP
        self.distinguished_users = []  # ✨ قائمة المتميزين (محميين من التفاعلات)
        self.muted_users = {}  # المستخدمين المكتومين
        self.frozen_users = {}  # المستخدمين المجمدين
        self.user_floors = {}   # تتبع طابق كل مستخدم للنقل الذكي
        self.warned_users = {}  # المستخدمين المحذرين
        self.auto_mod = True  # التحكم التلقائي
        self.spam_protection = True  # الحماية من السبام
        self.user_messages = {}  # تتبع رسائل المستخدمين للحماية من السبام
        self.interaction_history = set()  # 📨 مستخدمين تفاعلوا مع البوت (رسائل خاصة أو جولد)
        self.welcome_message = "نورت روم المنتجع 🌿✨"  # رسالة الترحيب الافتراضية
        self.custom_welcomes = {}   # رسائل ترحيب خاصة لأشخاص محددين
        self.welcome_public = True  # الترحيب في الشات العام
        self.banned_words = []  # الكلمات المحظورة
        
        # 🏢 إحداثيات الطوابق (تم ضبطها بدقة حسب الصور)
        self.floors = {
            "ground": Position(15.5, 0.25, 14.5, "FrontRight"),      # الأرضية
            "floor1": Position(12.5, 8.25, 17.0, "FrontRight"),     # فوق
            "floor2": Position(10.5, 17.5, 11.0, "FrontLeft"),    # فوق2
            "vip": Position(12.0, 13.75, 0.5, "FrontLeft"),        # VIP
        }
        
        # 🤖 موقع البوت الافتراضي
        self.bot_position = Position(15.5, 0.25, 14.5, "FrontRight")
        self.config_file = "bot_config.json"
        self.load_config()
        
        # 🎭 نظام الرقصات - أسماء نصية مع دعم للأرقام عبر القائمة
        self.emotes = {
            "Floating": {"id": "emote-float", "dur": 8, "ar": ["طفو", "تحليق"]},
            "SleighRide": {"id": "emote-sleigh", "dur": 9, "ar": ["زلاجة", "تزلج"]},
            "EmoteFashionista": {"id": "emote-fashionista", "dur": 5, "ar": ["فاشن", "موضة"]},
            "Cheerful": {"id": "emote-pose8", "dur": 4, "ar": ["مبتهج", "بهجة"]},
            "DanceIcecream": {"id": "dance-icecream", "dur": 14, "ar": ["ايسكريم", "بوظة"]},
            "Macarena": {"id": "dance-macarena", "dur": 12, "ar": ["ماكرينا", "مكارينا"]},
            "EmbracingModel": {"id": "emote-pose7", "dur": 4, "ar": ["موديل_احتضان"]},
            "ShuffleDance": {"id": "dance-tiktok10", "dur": 8, "ar": ["شافل", "خلط"]},
            "LambisPose": {"id": "emote-superpose", "dur": 4, "ar": ["بوز_سوبر"]},
            "GraveDance": {"id": "dance-weird", "dur": 21, "ar": ["رقص_غريب"]},
            "ViralGroove": {"id": "dance-tiktok9", "dur": 11, "ar": ["فايرال", "رقص_تيك"]},
            "EmoteCute": {"id": "emote-cute", "dur": 6, "ar": ["كيوت", "لطيف"]},
            "TheWave": {"id": "emote-wave", "dur": 2.5, "ar": ["موجة", "هاي"]},
            "Kiss": {"id": "emote-kiss", "dur": 2, "ar": ["بوسه", "قبلة", "بوس"]},
            "Laugh": {"id": "emote-laughing", "dur": 2.5, "ar": ["ضحك", "هههه"]},
            "Sweating": {"id": "emote-hot", "dur": 4, "ar": ["عرق", "حر"]},
            "ImACutie": {"id": "emote-cutey", "dur": 3, "ar": ["كيوتي", "حلو"]},
            "FashionPose": {"id": "emote-pose5", "dur": 4, "ar": ["بوز_فاشن"]},
            "Teleport": {"id": "emote-teleporting", "dur": 11, "ar": ["تليبورت", "انتقال"]},
            "LetsGoShopping": {"id": "dance-shoppingcart", "dur": 4, "ar": ["تسوق", "شوبنق"]},
            "GreedyEmote": {"id": "emote-greedy", "dur": 4, "ar": ["طماع", "جشع"]},
            "IChallengeYou": {"id": "emote-pose3", "dur": 5, "ar": ["تحدي"]},
            "FlirtyWink": {"id": "emote-pose1", "dur": 2, "ar": ["غمز"]},
            "EmotePunkguitar": {"id": "emote-punkguitar", "dur": 9, "ar": ["قيتار_بانك", "جيتار"]},
            "SingAlong": {"id": "idle_singing", "dur": 9.5, "ar": ["غناء", "اغنية"]},
            "ACasualDance": {"id": "idle-dance-casual", "dur": 8.5, "ar": ["رقص_عادي"]},
            "Confusion": {"id": "emote-confused", "dur": 8, "ar": ["حيرة", "محتار"]},
            "RaiseTheRoof": {"id": "emoji-celebrate", "dur": 3, "ar": ["سقف", "رفع_السقف"]},
            "SaunterSway": {"id": "dance-anime", "dur": 8, "ar": ["انمي", "رقص_انمي"]},
            "SwordFight": {"id": "emote-swordfight", "dur": 5, "ar": ["سيف", "قتال"]},
            "BashfulBlush": {"id": "emote-shy2", "dur": 4.5, "ar": ["خجل", "استحياء"]},
            "SaySoDance": {"id": "idle-dance-tiktok4", "dur": 15, "ar": ["سي_سو", "تيكتوك4"]},
            "DontStartNow": {"id": "dance-tiktok2", "dur": 10, "ar": ["تيكتوك2"]},
            "Model": {"id": "emote-model", "dur": 6, "ar": ["موديل", "عارض"]},
            "Charging": {"id": "emote-charging", "dur": 8, "ar": ["شحن", "طاقة"]},
            "DoTheWorm": {"id": "emote-snake", "dur": 5, "ar": ["دودة", "ثعبان"]},
            "RussianDance": {"id": "dance-russian", "dur": 10.25, "ar": ["رقص_روسي", "روسي"]},
            "UWUMood": {"id": "idle-uwu", "dur": 24, "ar": ["يو_دبليو_يو"]},
            "Clap": {"id": "emoji-clapping", "dur": 2, "ar": ["تصفيقة"]},
            "Happy": {"id": "emote-happy", "dur": 2, "ar": ["سعيد", "فرحان"]},
            "DanceWrong": {"id": "dance-wrong", "dur": 12, "ar": ["رقص_غلط"]},
            "TummyAche": {"id": "emoji-gagging", "dur": 5, "ar": ["مغص", "بطن"]},
            "SavageDance": {"id": "dance-tiktok8", "dur": 10, "ar": ["سافج", "وحشي"]},
            "KPopDance": {"id": "dance-blackpink", "dur": 6.5, "ar": ["كيبوب"]},
            "PennysDance": {"id": "dance-pennywise", "dur": 0.5, "ar": ["بيني"]},
            "Bow": {"id": "emote-bow", "dur": 3, "ar": ["انحناء", "انحناءة"]},
            "Curtsy": {"id": "emote-curtsy", "dur": 2, "ar": ["تنوره", "انحناءه"]},
            "SnowballFight": {"id": "emote-snowball", "dur": 5, "ar": ["ثلج", "كرة_ثلج"]},
            "SnowAngel": {"id": "emote-snowangel", "dur": 6, "ar": ["ملاك_ثلج"]},
            "Telekinesis": {"id": "emote-telekinesis", "dur": 10, "ar": ["تحريك_عقلي"]},
            "Maniac": {"id": "emote-maniac", "dur": 4.5, "ar": ["مجنون", "جنون"]},
            "EnergyBall": {"id": "emote-energyball", "dur": 7, "ar": ["كرة_طاقة"]},
            "FroggieHop": {"id": "demote-frog", "dur": 14, "ar": ["ضفدع", "نط_ضفدع"]},
            "Sit": {"id": "idle-loop-sitfloor", "dur": 22, "ar": ["جلوس", "اجلس", "قعود"]},
            "Hyped": {"id": "emote-hyped", "dur": 7, "ar": ["حماس", "متحمس"]},
            "JingleHop": {"id": "dance-jinglebell", "dur": 10.5, "ar": ["جنقل", "عيد_الميلاد"]},
            "BitNervous": {"id": "idle-nervous", "dur": 21, "ar": ["عصبي", "توتر"]},
            "GottaGo": {"id": "idle-toilet", "dur": 31.5, "ar": ["حمام", "لازم_اروح"]},
            "ZeroGravity": {"id": "emote-astronaut", "dur": 13, "ar": ["فضاء", "رائد"]},
            "Timejump": {"id": "emote-timejump", "dur": 4, "ar": ["قفز_زمني"]},
            "GroovyPenguin": {"id": "dance-pinguin", "dur": 11, "ar": ["بطريق", "بنغوين"]},
            "CreepyPuppet": {"id": "dance-creepypuppet", "dur": 6, "ar": ["دمية_مخيفة"]},
            "EmoteGravity": {"id": "emote-gravity", "dur": 8, "ar": ["جاذبية"]},
            "ZombieRun": {"id": "emote-zombierun", "dur": 9, "ar": ["ركض_زومبي"]},
            "Enthused": {"id": "idle-enthusiastic", "dur": 15, "ar": ["متحمس_جدا", "حماسة"]},
            "KawaiiGoGo": {"id": "dance-kawai", "dur": 10, "ar": ["كاواي"]},
            "Repose": {"id": "sit-relaxed", "dur": 29, "ar": ["استرخاء", "راحة"]},
            "Shy": {"id": "emote-shy", "dur": 4, "ar": ["خجول", "استحي"]},
            "No": {"id": "emote-no", "dur": 2, "ar": ["لا", "رفض"]},
            "Sad": {"id": "emote-sad", "dur": 4.5, "ar": ["حزين", "زعلان", "حزن"]},
            "Yes": {"id": "emote-yes", "dur": 2, "ar": ["نعم", "اي", "موافق"]},
            "Hello": {"id": "emote-hello", "dur": 2.5, "ar": ["مرحبا", "هلا", "اهلا"]},
            "Tired": {"id": "emote-tired", "dur": 4, "ar": ["تعبان", "تعب"]},
            "Angry": {"id": "emoji-angry", "dur": 5, "ar": ["غاضب", "معصب", "غضب"]},
            "ThumbsUp": {"id": "emoji-thumbsup", "dur": 2, "ar": ["ابهام", "ممتاز"]},
            "Stargazing": {"id": "emote-stargazer", "dur": 7, "ar": ["نجوم", "تامل_نجوم"]},
            "AirGuitar": {"id": "idle-guitar", "dur": 12, "ar": ["قيتار", "جيتار_هوائي"]},
            "Revelations": {"id": "emote-headblowup", "dur": 11, "ar": ["صدمة", "انفجار_راس"]},
            "WatchYourBack": {"id": "emote-creepycute", "dur": 7, "ar": ["انتبه", "خلف"]},
            "Arabesque": {"id": "emote-pose10", "dur": 3.5, "ar": ["ارابيسك"]},
            "PartyTime": {"id": "emote-celebrate", "dur": 3, "ar": ["حفلة", "احتفال"]},
            "IceSkating": {"id": "emote-iceskating", "dur": 7, "ar": ["تزلج_جليد"]},
            "ReadyToRumble": {"id": "emote-boxer", "dur": 5, "ar": ["ملاكمة", "بوكس"]},
            "Scritchy": {"id": "idle-wild", "dur": 25, "ar": ["حكة", "هرش"]},
            "ThisIsForYou": {"id": "emote-gift", "dur": 5, "ar": ["هدية", "هديه"]},
            "PushIt": {"id": "dance-employee", "dur": 6, "ar": ["دفع", "ادفع"]},
            "BigSurprise": {"id": "emote-pose6", "dur": 5, "ar": ["مفاجأة", "مفاجاة"]},
            "SweetLittleMoves": {"id": "dance-touch", "dur": 11, "ar": ["حركات_حلوة"]},
            "CelebrationStep": {"id": "emote-celebrationstep", "dur": 3, "ar": ["خطوة_احتفال"]},
            "Launch": {"id": "emote-launch", "dur": 9, "ar": ["اطلاق", "انطلاق"]},
            "CuteSalute": {"id": "emote-cutesalute", "dur": 2.5, "ar": ["تحية_لطيفة"]},
            "AtAttention": {"id": "emote-salute", "dur": 3, "ar": ["تحية", "سلام"]},
            "WopDance": {"id": "dance-tiktok11", "dur": 9, "ar": ["ووب", "تيكتوك11"]},
            "DitzyPose": {"id": "emote-pose9", "dur": 4, "ar": ["بوز_دتزي"]},
            "SweetSmooch": {"id": "emote-kissing", "dur": 5, "ar": ["بوسه_حلوة"]},
            "FairyFloat": {"id": "idle-floating", "dur": 24, "ar": ["طيران_خيالي", "جنية"]},
            "FairyTwirl": {"id": "emote-looping", "dur": 7, "ar": ["دوران_جنية"]},
            "Casting": {"id": "fishing-cast", "dur": 1, "ar": ["صيد_رمي"]},
            "NowWeWait": {"id": "fishing-idle", "dur": 15, "ar": ["انتظار_صيد"]},
            "MiningMine": {"id": "mining-mine", "dur": 3, "ar": ["تعدين"]},
            "LandingAFish": {"id": "fishing-pull", "dur": 1, "ar": ["سحب_سمكة"]},
            "WeHaveAStrike": {"id": "fishing-pull-small", "dur": 1, "ar": ["سمكة_صغيرة"]},
            "MiningSuccess": {"id": "mining-success", "dur": 3, "ar": ["تعدين_ناجح"]},
            "IgnitionBoost": {"id": "hcc-jetpack", "dur": 19, "ar": ["جت_باك", "صاروخ"]},
            "Rest": {"id": "sit-open", "dur": 26.025963, "ar": ["ريست", "راحه"]},
            "ريست": {"id": "sit-open", "dur": 26.025963, "ar": ["ريست", "راحه"]},
            "Aerobics": {"id": "idle-loop-aerobics", "dur": 8, "ar": ["ايروبكس", "رياضه"]},
            "Amused": {"id": "emote-laughing2", "dur": 5, "ar": ["مستمتع", "ضحك2"]},
            "Arrogance": {"id": "emoji-arrogance", "dur": 6, "ar": ["غرور", "تكبر"]},
            "Attentive": {"id": "idle_layingdown", "dur": 24, "ar": ["منتبه", "مستلقي"]},
            "BlastOff": {"id": "emote-disappear", "dur": 6, "ar": ["اختفاء", "انطلق"]},
            "Boo": {"id": "emote-boo", "dur": 4, "ar": ["بوو", "تخويف"]},
            "Cheer": {"id": "dance-cheerleader", "dur": 17, "ar": ["تشجيع"]},
            "CozyNap": {"id": "idle-floorsleeping", "dur": 13, "ar": ["قيلولة", "نوم_ارض"]},
            "Dab": {"id": "emote-dab", "dur": 2, "ar": ["داب"]},
            "DuckWalk": {"id": "dance-duckwalk", "dur": 11, "ar": ["مشي_بطة", "بطة"]},
            "ElbowBump": {"id": "emote-elbowbump", "dur": 3, "ar": ["كوع"]},
            "FallingApart": {"id": "emote-apart", "dur": 4, "ar": ["تفكك", "انهيار"]},
            "Fighter": {"id": "idle-fighter", "dur": 17, "ar": ["مقاتل"]},
            "FruityDance": {"id": "dance-fruity", "dur": 16, "ar": ["رقص_فواكه"]},
            "GangnamStyle": {"id": "emote-gangnam", "dur": 6.5, "ar": ["جانجنام", "كانكنام"]},
            "Gasp": {"id": "emoji-scared", "dur": 2.5, "ar": ["خوف", "فزع"]},
            "Ghost": {"id": "emoji-ghost", "dur": 3, "ar": ["شبح"]},
            "GhostFloat": {"id": "emote-ghost-idle", "dur": 19, "ar": ["جوست", "شبح_طائر"]},
            "جوست": {"id": "emote-ghost-idle", "dur": 19, "ar": ["جوست", "شبح_طائر"]},
            "GimmeAttention": {"id": "emote-attention", "dur": 4, "ar": ["انتباه", "اهتمام"]},
            "Handstand": {"id": "emote-handstand", "dur": 3.5, "ar": ["وقوف_يدين"]},
            "HarlemShake": {"id": "emote-harlemshake", "dur": 13, "ar": ["هارلم_شيك"]},
            "HipShake": {"id": "dance-hipshake", "dur": 12, "ar": ["هز_وسط"]},
            "ImaginaryJetpack": {"id": "emote-jetpack", "dur": 16, "ar": ["جت_باك_خيالي"]},
            "Irritated": {"id": "idle-angry", "dur": 24, "ar": ["متضايق"]},
            "KarmaDance": {"id": "dance-wild", "dur": 13, "ar": ["كارما", "رقص_بري"]},
            "LaidBack": {"id": "sit-open", "dur": 25, "ar": ["مسترخي"]},
            "Levitate": {"id": "emoji-halo", "dur": 5.5, "ar": ["تحليق_هالة", "هالة"]},
            "LoveFlutter": {"id": "emote-hearteyes", "dur": 3.5, "ar": ["عيون_قلب", "حب_عيون"]},
            "Lying": {"id": "emoji-lying", "dur": 5.5, "ar": ["كذب", "كذاب"]},
            "Magnetic": {"id": "dance-tiktok14", "dur": 9.5, "ar": ["مغناطيس"]},
            "MindBlown": {"id": "emoji-mind-blown", "dur": 2, "ar": ["عقل_منفجر", "ذهول"]},
            "MoonlitHowl": {"id": "emote-howl", "dur": 5.5, "ar": ["عواء"]},
            "Moonwalk": {"id": "emote-gordonshuffle", "dur": 7.5, "ar": ["مون_ووك", "مونووك"]},
            "NightFever": {"id": "emote-nightfever", "dur": 5, "ar": ["حمى_الليل"]},
            "NinjaRun": {"id": "emote-ninjarun", "dur": 4, "ar": ["نينجا", "ركض_نينجا"]},
            "NocturnalHowl": {"id": "idle-howl", "dur": 30, "ar": ["عواء_ليلي"]},
            "OrangeJuiceDance": {"id": "dance-orangejustice", "dur": 5.5, "ar": ["عصير_برتقال"]},
            "Panic": {"id": "emote-panic", "dur": 2, "ar": ["هلع", "ذعر"]},
            "Peekaboo": {"id": "emote-peekaboo", "dur": 3.5, "ar": ["بيكابو", "استغماية"]},
            "PissedOff": {"id": "emote-frustrated", "dur": 4.5, "ar": ["زهق", "منرفز"]},
            "PossessedPuppet": {"id": "emote-puppet", "dur": 16, "ar": ["دمية"]},
            "Punch": {"id": "emoji-punch", "dur": 1, "ar": ["لكمة", "لكم"]},
            "PushUps": {"id": "dance-aerobics", "dur": 8, "ar": ["تمارين", "جيم", "رياضة"]},
            "Rainbow": {"id": "emote-rainbow", "dur": 2.5, "ar": ["قوس_قزح"]},
            "Relaxed": {"id": "idle_layingdown2", "dur": 20.5, "ar": ["استرخاء2"]},
            "Relaxing": {"id": "idle-floorsleeping2", "dur": 16, "ar": ["استرخاء_نوم"]},
            "Renegade": {"id": "idle-dance-tiktok7", "dur": 12, "ar": ["رينيقيد"]},
            "Revival": {"id": "emote-death", "dur": 6, "ar": ["احياء", "موت"]},
            "RingOnIt": {"id": "dance-singleladies", "dur": 20.5, "ar": ["خاتم", "سنقل_ليديز"]},
            "ROFL": {"id": "emote-rofl", "dur": 6, "ar": ["ضحك_تدحرج"]},
            "Robot": {"id": "emote-robot", "dur": 7, "ar": ["روبوت", "ربوت"]},
            "RockOut": {"id": "dance-metal", "dur": 14.5, "ar": ["روك", "ميتال"]},
            "Roll": {"id": "emote-roll", "dur": 3, "ar": ["تدحرج"]},
            "SecretHandshake": {"id": "emote-secrethandshake", "dur": 3, "ar": ["مصافحة_سرية"]},
            "Shrink": {"id": "emote-shrink", "dur": 8, "ar": ["تقلص", "صغر"]},
            "Slap": {"id": "emote-slap", "dur": 2, "ar": ["صفعة", "كف"]},
            "Smoothwalk": {"id": "dance-smoothwalk", "dur": 5.5, "ar": ["مشي_ناعم"]},
            "Stinky": {"id": "emoji-poop", "dur": 4, "ar": ["نتن", "ريحة"]},
            "SuperKick": {"id": "emote-kicking", "dur": 4.5, "ar": ["رفسة", "رفس"]},
            "SuperRun": {"id": "emote-superrun", "dur": 6, "ar": ["ركض_سريع"]},
            "TapDance": {"id": "emote-tapdance", "dur": 10.5, "ar": ["رقص_تاب"]},
            "TapLoop": {"id": "idle-loop-tapdance", "dur": 6, "ar": ["تاب_لوب"]},
            "Trampoline": {"id": "emote-trampoline", "dur": 5, "ar": ["ترامبولين", "نطاطة"]},
            "ZombieDance": {"id": "dance-zombie", "dur": 12, "ar": ["رقص_زومبي"]},
            "Annoyed": {"id": "idle-loop-annoyed", "dur": 16.5, "ar": ["منزعج2", "ازعاج"]},
            "Bummed": {"id": "idle-loop-sad", "dur": 28, "ar": ["محبط", "كئيب"]},
            "BunnyHop": {"id": "emote-bunnyhop", "dur": 11, "ar": ["ارنب", "نط_ارنب"]},
            "Chillin": {"id": "idle-loop-happy", "dur": 18, "ar": ["رايق", "مرتاح"]},
            "Clumsy": {"id": "emote-fail2", "dur": 6, "ar": ["اخرق", "وقعة"]},
            "Collapse": {"id": "emote-death2", "dur": 4, "ar": ["انهيار2", "سقوط"]},
            "Cold": {"id": "emote-cold", "dur": 3, "ar": ["برد", "بارد"]},
            "Disco": {"id": "emote-disco", "dur": 4.5, "ar": ["ديسكو"]},
            "Embarrassed": {"id": "emote-embarrassed", "dur": 7, "ar": ["محرج", "احراج"]},
            "Exasperated": {"id": "emote-exasperated", "dur": 2, "ar": ["مستاء"]},
            "EyeRoll": {"id": "emoji-eyeroll", "dur": 2.5, "ar": ["تدوير_عيون"]},
            "FacePalm": {"id": "emote-exasperatedb", "dur": 2, "ar": ["فيس_بالم"]},
            "Faint": {"id": "emote-fainting", "dur": 17.5, "ar": ["اغماء", "اغماءة"]},
            "FaintDrop": {"id": "emote-deathdrop", "dur": 3, "ar": ["سقوط_مفاجئ"]},
            "Fall": {"id": "emote-fail1", "dur": 5.5, "ar": ["وقوع", "طيحة"]},
            "Fatigued": {"id": "idle-loop-tired", "dur": 21, "ar": ["ارهاق", "مرهق"]},
            "FeelTheBeat": {"id": "idle-dance-headbobbing", "dur": 24.5, "ar": ["ايقاع", "هز_راس"]},
            "FireballLunge": {"id": "emoji-hadoken", "dur": 2, "ar": ["كرة_نار", "هادوكن"]},
            "GiveUp": {"id": "emoji-give-up", "dur": 5, "ar": ["استسلام", "يأس"]},
            "HandsInTheAir": {"id": "dance-handsup", "dur": 21.5, "ar": ["ايدين_فوق"]},
            "HeartHands": {"id": "emote-heartfingers", "dur": 3.5, "ar": ["قلب_بالايد"]},
            "HeroPose": {"id": "idle-hero", "dur": 21, "ar": ["بطل", "سوبرمان"]},
            "HomeRun": {"id": "emote-baseball", "dur": 6.5, "ar": ["بيسبول"]},
            "HugYourself": {"id": "emote-hugyourself", "dur": 4.5, "ar": ["حضن_نفسك"]},
            "IBelieveICanFly": {"id": "emote-wings", "dur": 12.5, "ar": ["اجنحة", "طيران"]},
            "Jump": {"id": "emote-jumpb", "dur": 3, "ar": ["قفز", "نط"]},
            "JudoChop": {"id": "emote-judochop", "dur": 2, "ar": ["جودو", "كاراتيه"]},
            "LevelUp": {"id": "emote-levelup", "dur": 5.5, "ar": ["ترقية", "ليفل_اب"]},
            "MonsterFail": {"id": "emote-monster_fail", "dur": 4, "ar": ["وحش_فشل"]},
            "Naughty": {"id": "emoji-naughty", "dur": 4, "ar": ["شقي", "مشاغب"]},
            "PartnerHeartArms": {"id": "emote-heartshape", "dur": 5.5, "ar": ["قلب_ايدين"]},
            "PartnerHug": {"id": "emote-hug", "dur": 3, "ar": ["حضن", "عناق"]},
            "Peace": {"id": "emote-peace", "dur": 5, "ar": ["سلام_علامة", "بيس"]},
            "Point": {"id": "emoji-there", "dur": 1.5, "ar": ["اشارة", "هناك"]},
            "Ponder": {"id": "idle-lookup", "dur": 21, "ar": ["تفكير", "تأمل"]},
            "Posh": {"id": "idle-posh", "dur": 21, "ar": ["فخم", "اناقة"]},
            "PoutyFace": {"id": "idle-sad", "dur": 24, "ar": ["زعل", "وجه_حزين"]},
            "Pray": {"id": "emoji-pray", "dur": 4, "ar": ["دعاء", "صلاة"]},
            "Proposing": {"id": "emote-proposing", "dur": 4, "ar": ["خطبة", "عرض_زواج"]},
            "RopePull": {"id": "emote-ropepull", "dur": 8, "ar": ["سحب_حبل"]},
            "Sick": {"id": "emoji-sick", "dur": 4.5, "ar": ["مريض"]},
            "Sleepy": {"id": "idle-sleep", "dur": 38, "ar": ["نوم", "نعسان"]},
            "Smirk": {"id": "emoji-smirking", "dur": 4, "ar": ["ابتسامة_ماكرة"]},
            "Sneeze": {"id": "emoji-sneeze", "dur": 2.5, "ar": ["عطس", "عطاس"]},
            "Sob": {"id": "emoji-crying", "dur": 3, "ar": ["بكاء", "بكى"]},
            "SplitsDrop": {"id": "emote-splitsdrop", "dur": 4, "ar": ["سبليت", "شقلبة"]},
            "Stunned": {"id": "emoji-dizzy", "dur": 3.5, "ar": ["مذهول", "دوخة"]},
            "SumoFight": {"id": "emote-sumo", "dur": 10, "ar": ["سومو"]},
            "SuperPunch": {"id": "emote-superpunch", "dur": 3, "ar": ["لكمة_خارقة"]},
            "Theatrical": {"id": "emote-theatrical", "dur": 8, "ar": ["مسرحي", "تمثيل"]},
            "Think": {"id": "emote-think", "dur": 3, "ar": ["تفكير2", "فكر"]},
            "ThumbSuck": {"id": "emote-suckthumb", "dur": 3.5, "ar": ["مص_ابهام"]},
            "VogueHands": {"id": "dance-voguehands", "dur": 8.5, "ar": ["فوغ"]},
            "WiggleDance": {"id": "dance-sexy", "dur": 11.5, "ar": ["هز", "رقص_مثير"]},
            "Zombie": {"id": "idle_zombie", "dur": 28, "ar": ["زومبي"]},
            "DanceShuffle": {"id": "dance-shuffle", "dur": 7, "ar": ["شافل2"]},
            "EmoteConfused2": {"id": "emote-confused2", "dur": 7, "ar": ["حيرة2"]},
            "EmoteFail3": {"id": "emote-fail3", "dur": 6, "ar": ["فشل"]},
            "EmoteReceiveDisappointed": {"id": "emote-receive-disappointed", "dur": 5.5, "ar": ["خيبة_امل"]},
            "EmoteReceiveHappy": {"id": "emote-receive-happy", "dur": 4, "ar": ["استلام_سعيد"]},
            "IdleCold": {"id": "idle-cold", "dur": 10, "ar": ["برد_شديد"]},
            "IdleTough": {"id": "idle_tough", "dur": 10, "ar": ["قوي", "صلب"]},
            "MiningFail": {"id": "mining-fail", "dur": 2.5, "ar": ["تعدين_فاشل"]},
            "RunVertical": {"id": "run-vertical", "dur": 1, "ar": ["ركض_عمودي"]},
            "Shy2": {"id": "emote-shy2", "dur": 4.5, "ar": ["خجل2", "شاي2"]},
            "swag": {"id": "dance-swagbounce", "dur": 10, "ar": ["سواج", "سواغ"]},
            "floss": {"id": "dance-floss", "dur": 21, "ar": ["فلوس", "خيط"]},
            "PopularVibe": {"id": "dance-popularvibe", "dur": 10, "ar": ["بوبيولار", "فايب"]},
            "Twerk": {"id": "dance-twerk", "dur": 10, "ar": ["تويرك", "تيرك"]},
            "Griddy": {"id": "dance-griddy", "dur": 10, "ar": ["جريدي", "قهر"]},
            "TrueHeart": {"id": "dance-true-heart", "dur": 10, "ar": ["قلب_حقيقي", "قلب2"]},
        }
        
        
        #  نظام التفاعلات (تفاعل موجه: لاعب -> لاعب آخر)
        # الصيغة: المفتاح هو اسم التفاعل بالانجليزي وعربي
        # "command": {"id": "action_emote", "target_id": "reaction_emote", "ar": ["اسم_عربي"], "en": ["english_name"]}
        # 🤼 نظام التفاعلات (تفاعل موجه: لاعب -> لاعب آخر)
        # الصيغة: المفتاح هو اسم التفاعل بالانجليزي وعربي
        # "command": {"id": "action_emote", "target_id": "reaction_emote", "ar": ["اسم_عربي"], "en": ["english_name"], "dur": duration}
        self.interactions = {
            "slap": {"id": "emote-slap", "target_id": "emote-fail2", "ar": ["كف", "صفعة"], "en": ["slap"], "dur": 2},
            "kiss": {"id": "emote-kiss", "target_id": "emote-kissing", "ar": ["بوس", "قبلة"], "en": ["kiss"], "dur": 2},
            "hug": {"id": "emote-hug", "target_id": "emote-hug", "ar": ["حضن", "عناق"], "en": ["hug"], "dur": 3},
            "punch": {"id": "emote-superpunch", "target_id": "emote-death2", "ar": ["لكم", "بوكس"], "en": ["punch"], "dur": 3},
            "kick": {"id": "emote-kicking", "target_id": "emote-fail1", "ar": ["ركل", "رفس"], "en": ["kick"], "dur": 4.5},
            "stab": {"id": "emote-swordfight", "target_id": "emote-death", "ar": ["طعن", "سيف"], "en": ["stab"], "dur": 5},
            "shoot": {"id": "emote-energyball", "target_id": "emote-deathdrop", "ar": ["اطلاق", "نار"], "en": ["shoot"], "dur": 7},
            "bite": {"id": "emote-zombierun", "target_id": "emote-fainting", "ar": ["عض", "عضة"], "en": ["bite"], "dur": 5},
            "worship": {"id": "emote-bow", "target_id": "emote-curtsy", "ar": ["احترام", "تقدير"], "en": ["worship"], "dur": 3},
            "scare": {"id": "emote-boo", "target_id": "emoji-scared", "ar": ["تخويف", "بو"], "en": ["scare"], "dur": 4},
            "laugh": {"id": "emote-laughing", "target_id": "emote-embarrassed", "ar": ["ضحك", "سخرية"], "en": ["laugh_at"], "dur": 2.5},
            "flirt": {"id": "emote-heartfingers", "target_id": "emote-shy2", "ar": ["مغازلة", "غزل"], "en": ["flirt"], "dur": 3.5},
            "highfive": {"id": "emote-celebrate", "target_id": "emote-celebrate", "ar": ["كفك", "هاي فايف"], "en": ["highfive"], "dur": 3},
            "propose": {"id": "emote-proposing", "target_id": "emote-superpose", "ar": ["زواج", "خطبة"], "en": ["propose"], "dur": 4},
        }
        
        # إنشاء قائمة بالأرقام (قبل التنظيف) للحفاظ على ثبات الأرقام (مثل 210 لـ Proposing)
        self.emote_list = [None] + list(self.emotes.values())

        # 🧹 تنظيف التضارب: حذف أي رقصة عادية لها نفس اسم تفاعل (للبحث النصي فقط)
        for interaction_name, interaction_data in self.interactions.items():
            # حذف الاسم الإنجليزي
            if interaction_name in self.emotes:
                del self.emotes[interaction_name]
            
            # فحص الأسماء العربية في الرقصات
            keys_to_remove = []
            for emote_key, emote_data in self.emotes.items():
                if any(ar in emote_data.get("ar", []) for ar in interaction_data["ar"]):
                   keys_to_remove.append(emote_key)
            
            for k in keys_to_remove:
                del self.emotes[k]

        # قائمة لتتبع المستخدمين الراقصين (لإيقافهم عند كتابة 0)

        
                # قائمة لتتبع المستخدمين الراقصين (لإيقافهم عند كتابة 0)
        self.dancing_users = {}
        self.active_dance_requests = {} # لتتبع آخر طلب رقص لكل مستخدم ومنع التداخل
        
        # 💝 نظام الرياكشنات الرسمية من Highrise SDK
        # الأنواع المتاحة: "clap", "heart", "thumbs", "wave", "wink"
        self.reactions = {
            "heart": {"ar": ["قلب", "ق", "حب", "ح", "h"]},
            "thumbs": {"ar": ["اعجاب", "ا", "لايك", "ثامز", "thumbs"]},
            "clap": {"ar": ["تصفيق", "ت", "كلاب", "clap"]},
            "wave": {"ar": ["تلويح", "تل", "باي", "wave"]},
            "wink": {"ar": ["غمزة", "غ", "وينك", "wink"]},
        }


        
        # البوت يرقص تلقائياً
        self.bot_dancing = False
        self.bot_dance_task = None
        
        # نظام إعادة الاتصال
        self.connection_active = True
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 999  # محاولات غير محدودة تقريباً


    def load_config(self):
        """Load bot configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # تحميل الموقع
                    pos = config.get("bot_position")
                    if pos:
                        self.bot_position = Position(pos["x"], pos["y"], pos["z"], pos.get("facing", "FrontRight"))
                    
                    # تحميل الملاك والمشرفين (إذا وجدت)
                    self.admins = config.get("admins", self.admins)
                    self.owners = config.get("owners", self.owners)
                    self.vip_users = config.get("vip_users", [])
                    self.distinguished_users = config.get("distinguished_users", [])
                    
                    # تحميل الترحيبات الخاصة
                    self.custom_welcomes = config.get("custom_welcomes", {})
                    
                    # تحميل إعدادات الترحيب العام
                    self.welcome_message = config.get("welcome_message", self.welcome_message)
                    self.welcome_public = config.get("welcome_public", self.welcome_public)
                    
                print("Configuration loaded successfully")
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        """Save bot configuration to JSON file"""
        try:
            config = {
                "bot_position": {
                    "x": self.bot_position.x,
                    "y": self.bot_position.y,
                    "z": self.bot_position.z,
                    "facing": self.bot_position.facing
                },
                "admins": self.admins,
                "owners": self.owners,
                "vip_users": self.vip_users,
                "distinguished_users": self.distinguished_users,
                "custom_welcomes": self.custom_welcomes,
                "welcome_message": self.welcome_message,
                "welcome_public": self.welcome_public
            }
            with open(self.config_file, "w", encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print("Configuration saved successfully")
        except Exception as e:
            print(f"Error saving config: {e}")

    async def safe_chat(self, msg: str):
        try:
            # Highrise chat limit is around 255 characters
            if len(msg) > 255: msg = msg[:252] + "..."
            await self.highrise.chat(msg)
        except: pass

    async def safe_whisper(self, uid: str, msg: str):
        try:
            # Highrise whisper limit is around 255 characters
            if len(msg) > 255: msg = msg[:252] + "..."
            await self.highrise.send_whisper(uid, msg)
        except: pass

    async def on_start(self, session_metadata: SessionMetadata):
        """When the bot starts"""
        print(f"Bot connected to room as: {session_metadata.user_id}")
        print(f"Room name: {session_metadata.room_info.room_name}")
        
        # إلغاء أي مهام سابقة لتجنب التكرار عند إعادة الاتصال
        if hasattr(self, 'bot_dance_task') and self.bot_dance_task:
            try:
                self.bot_dance_task.cancel()
            except: pass
            self.bot_dance_task = None
            
        # إعادة تعيين حالة الاتصال
        self.connection_active = True
        self.reconnect_attempts = 0
        
        # Move bot with retry loop to avoid "Not in room" errors
        max_retries = 6
        for attempt in range(max_retries):
            try:
                wait_time = 3 if attempt == 0 else (2 + attempt)
                if attempt > 0:
                    print(f"Movement attempt {attempt + 1}/{max_retries} (waiting {wait_time}s)...")
                await asyncio.sleep(wait_time)
                
                room_users = await self.highrise.get_room_users()
                users_list = getattr(room_users, 'content', [])
                bot_user = next((u for u, _ in users_list if u.id == self.highrise.my_id), None)
                
                if bot_user:
                    print(f"Bot found in room. Moving to: {self.bot_position}")
                    await self.highrise.teleport(bot_user.id, self.bot_position)
                    break
                else:
                    if attempt > 1:
                        print(f"Bot ID {self.highrise.my_id} not found in room users yet. Retrying...")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("Could not move bot. Proceeding...")

        # 👕 تعيين الملابس الجديدة (لبسة الصورة)
        try:
            outfit = [
                Item(type="clothing", amount=1, id="body-flesh", active_palette=1),   # لون البشرة
                Item(type="clothing", amount=1, id="hair_front-n_animecollection2018coolguyhair", active_palette=6),  # كريمي أبيض (اللون 6)
                Item(type="clothing", amount=1, id="hair_back-n_animecollection2018coolguyhair", active_palette=6),   # كريمي أبيض (اللون 6)
                Item(type="clothing", amount=1, id="eye-n_animecollection2018bishoneneyes"),                         # عيون انيمي
                Item(type="clothing", amount=1, id="eyebrow-n_08"),                                # حواجب
                Item(type="clothing", amount=1, id="nose-n_01"),                                   # أنف
                Item(type="clothing", amount=1, id="mouth-n_01"),                                  # فم
                Item(type="clothing", amount=1, id="fullsuit-n_eastershop2021overalls"),           # بدلة كاملة (الأوفيرول)
                Item(type="clothing", amount=1, id="handbag-n_MothersDay2018bouquet"),             # باقة ورد
                Item(type="clothing", amount=1, id="sock-n_seasonpass2026set3socks"),              # جوارب
                Item(type="clothing", amount=1, id="shoes-n_swimwear2018whiteslides"),             # صندل أبيض
            ]
            
            print("Trying to set final outfit...")
            await self.highrise.set_outfit(outfit)
            print("Set outfit command sent to server.")
            
        except Exception as e:
            print(f"Error in on_start outfit: {e}")

        # بدء رقص البوت التلقائي
        if not self.bot_dancing:
            self.bot_dancing = True
            self.bot_dance_task = asyncio.create_task(self.bot_auto_dance())

        # 💓 Keep-Alive
        if not hasattr(self, '_keepalive_task') or self._keepalive_task is None or self._keepalive_task.done():
            self._keepalive_task = asyncio.create_task(self._keep_alive_loop())
            print("💓 Keep-Alive started")

    async def _keep_alive_loop(self):
        """💓 Keep-Alive داخلي خفيف - يمنع Render من إيقاف البوت"""
        print("💓 Keep-Alive loop running...")
        while True:
            try:
                await asyncio.sleep(10 * 60)  # كل 10 دقائق
                import datetime
                print(f"💓 Keep-Alive | {datetime.datetime.now().strftime('%H:%M:%S')}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"💓 Keep-Alive error: {e}")
                await asyncio.sleep(30)

    async def on_user_join(self, user: User, position: Position):
        """When a new user joins"""
        print(f"User joined: {user.username}")
        
        # Sending a welcome heart
        try:
            await self.highrise.react("heart", user.id)
            print(f"Sent welcome heart to {user.username}")
        except Exception as e:
            print(f"Error sending welcome heart: {e}")
        
        # 🤖 البوت يرحب بالضيف (يقطع رقصة الفلوس ثم يعود لها)
        try:
            # 1. إيقاف رقصة الفلوس المؤقت
            if self.bot_dance_task and not self.bot_dance_task.done():
                self.bot_dance_task.cancel()
            
            # 2. البوت يقوم برقصة الترحيب (Wave)
            welcome_emote_id = "emote-wave"  # رقم 13
            welcome_duration = 2.5
            
            await self.highrise.send_emote(welcome_emote_id)
            print(f"Bot welcomes {user.username}")
            
            # 3. انتظار انتهاء الترحيب
            await asyncio.sleep(welcome_duration)
            
            # 4. العودة لرقصة الفلوس
            self.bot_dance_task = asyncio.create_task(self.bot_auto_dance())
            
        except Exception as e:
            print(f"Error in bot welcome: {e}")
            # Try to resume dance in case of error
            self.bot_dance_task = asyncio.create_task(self.bot_auto_dance())
        
        # --- ✨ نظام الترحيب الجديد ---
        try:
            # 1. إرسال الترحيب العام في الشات
            if self.welcome_message and self.welcome_public:
                await self.safe_chat(f"🎊 {self.welcome_message} @{user.username}")
            
            # 2. إرسال الترحيب الخاص في الهمس (قائمة الأوامر الأساسية)
            commands_msg = f"🌿 نورت المنتجع يا @{user.username}!\n📖 اكتب help لمعرفة الأوامر المتاحة لك."
            await self.safe_whisper(user.id, commands_msg)
                
        except Exception as e:
            print(f"Error in welcome sequence: {e}")


    async def on_user_leave(self, user: User):
        """When a user leaves"""
        print(f"User left: {user.username}")
        
        # مسح بيانات المستخدم من الذاكرة
        if user.id in self.user_messages:
            del self.user_messages[user.id]
        # ✅ الكتم يبقى حتى لو اللاعب طلع ورجع (لا نحذف muted_users)
        # ✅ التجميد يبقى حتى لو اللاعب طلع ورجع
        # if user.id in self.frozen_users:
        #     del self.frozen_users[user.id]
        if user.id in self.dancing_users:
            self.dancing_users[user.id].cancel()
            del self.dancing_users[user.id]
        

    
    def _get_floor_name(self, y: float, z: float = 0) -> str | None:
        """تحديد اسم الطابق (أرضي < 4، أول < 10، الطابق الثاني و VIP > 10)"""
        if y < 4.0:
            return "ground"
        elif 4.0 <= y < 10.0:
            return "floor1"
        elif y >= 10.0:
            # تمييز VIP بناءً على Z (VIP قريب من الصفر في Z حسب الإحداثيات الجديدة)
            if z < 3.0:
                return "vip"
            else:
                return "floor2"
        return None

    async def on_user_move(self, user: User, destination: Position | AnchorPosition):
        """عند تحرك مستخدم - للتحقق من التجميد والانتقال الذكي بين الطوابق"""
        # إذا كان المستخدم مجمد، نعيده لموقعه السابق
        if user.id in self.frozen_users:
            frozen_pos = self.frozen_users[user.id]
            await self.highrise.teleport(user.id, frozen_pos)
            return
        
        # نظام الانتقال الذكي بين الطوابق
        if not isinstance(destination, Position):
            return
            
        try:
            # تحديد الطابق الحالي والمستهدف
            current_floor = self.user_floors.get(user.id, "ground")
            target_floor = self._get_floor_name(destination.y, destination.z)
            
            facing = getattr(destination, 'facing', 'FrontRight') or 'FrontRight'
            print(f"Movement {user.username}: current={current_floor}, target={target_floor}")
            
            if target_floor is None:
                return
            
            # فقط ننقل إذا كان الطابق المستهدف مختلف عن الحالي
            if target_floor != current_floor:
                # التحقق من صلاحية طابق VIP (فقط إذا كان يحاول الدخول إليه من طابق آخر)
                if target_floor == "vip" and current_floor != "vip":
                    is_admin = await self.is_admin(user)
                    if not is_admin:
                        # إرسال اللاعب للطابق الأرضي إذا لم يكن مشرفاً وحاول الدخول للـ VIP
                        await self.highrise.teleport(user.id, self.floors["ground"])
                        self.user_floors[user.id] = "ground"
                        await self.highrise.send_whisper(user.id, "❌ طابق VIP مخصص للمشرفين فقط!")
                        return

                # تحديث الطابق الحالي فوراً لمنع التكرار
                self.user_floors[user.id] = target_floor
                
                floor_labels = {
                    "ground": "🏢 الطابق الأرضي",
                    "floor1": "🏬 فوق",
                    "floor2": "🏬 فوق2",
                    "vip": "💎 VIP"
                }

                floor_y = self.floors[target_floor].y
                
                # الانتقال فوراً لنفس النقطة التي تم النقر عليها ولكن بارتفاع الطابق الصحيح
                new_pos = Position(destination.x, floor_y, destination.z, facing)
                print(f"Smart Teleport: {current_floor} -> {target_floor} (Target Y: {floor_y})")
                await self.highrise.teleport(user.id, new_pos)
                await self.highrise.send_whisper(user.id, f"✨ تم نقلك إلى {floor_labels[target_floor]}")
            
            # إذا كان في نفس الطابق ولكن الارتفاع غير صحيح (متعلق بالـ snap للجاذبية أو الطيران)
            else:
                floor_y = self.floors[target_floor].y
                if abs(destination.y - floor_y) > 0.5:
                    new_pos = Position(destination.x, floor_y, destination.z, facing)
                    await self.highrise.teleport(user.id, new_pos)
                    print(f"Snap Teleport on {target_floor}")
            
            # التأكد من تحديث الحالة دائماً في الذاكرة
            self.user_floors[user.id] = target_floor
            
        except Exception as e:
            print(f"Error in teleport system: {e}")
            import traceback
            traceback.print_exc()

    async def on_chat(self, user: User, message: str):
        """عند استقبال رسالة في الشات"""
        try:
            msg_lower = message.lower().strip()
            
            # ✅ تجاهل رسائل البوت نفسه لمنع التكرار أو تنفيذ أوامر على نفسه
            if user.id == self.highrise.my_id:
                return

            # التحقق من المستخدم المكتوم
            if user.id in self.muted_users:
                await self.highrise.send_whisper(user.id, "🔇 أنت مكتوم! لا يمكنك الكتابة في الشات")
                return
            
            # رقم 0 = إيقاف الرقص (أعلى أولوية!)
            if message.strip() == "0":
                await self.stop_dance(user)
                return
            
            parts = message.strip().split()
            if not parts:
                return
            

            
            # 💫 نظام التفاعل المزدوج (Interaction System) - أولوية قصوى
            # الصيغة: <اسم_تفاعل> <يوزر> [لوب]
            if len(parts) >= 2:
                cmd = parts[0].lower()
                target_name = parts[1]
                is_loop = False
                
                # التحقق من وجود كلمة لوب
                if len(parts) >= 3 and parts[2].lower() in ["لوب", "loop", "تكرار"]:
                    is_loop = True

                # البحث في التفاعلات
                interaction_found = None
                for key, data in self.interactions.items():
                    if cmd in data["en"] or cmd in data["ar"]:
                        interaction_found = data
                        break
                
                if interaction_found:
                    await self.perform_interaction(user, target_name, interaction_found, is_loop)
                    return

            # 💫 نظام الرقص الثنائي القديم (رقصات عادية) - أولوية ثانية
            # الصيغة: <اسم_تفاعل> <يوزر>
            # شرط إضافي: الكلمة الثانية ليست "لوب" (لان ذلك يعني رقص فردي متكرر)
            if len(parts) >= 2 and parts[1].lower() not in ["loop", "لوب", "تكرار"]:
                # 💃 أولاً: فحص إذا كان رقم رقصة
                try:
                    dance_num = int(parts[0])
                    if 1 <= dance_num < len(self.emote_list):
                        # رقص ثنائي بالرقم (مع لوب)
                        await self.dance_with_user(user, parts[1], dance_num)
                        return
                except ValueError:
                    pass
                
                # ثانياً: فحص إذا كان اسم رقصة (إنجليزي أو عربي)
                first_word = parts[0].lower()
                
                for emote_key, emote in self.emotes.items():
                    # فحص الاسم الإنجليزي (مفتاح القاموس)
                    if emote_key.lower() == first_word:
                        await self.dance_with_user(user, parts[1], emote_key)
                        return
                    # فحص الأسماء العربية
                    for ar_name in emote.get("ar", []):
                        if ar_name.lower() == first_word:
                            await self.dance_with_user(user, parts[1], emote_key)
                            return
                

            
            # نظام الرياكشنات - أولوية عالية
            if len(parts) == 2:
                possible_reaction1 = parts[0].lower()
                target_username1 = parts[1]
                target_username2 = parts[0]
                possible_reaction2 = parts[1].lower()
                
                reaction_found = None
                target_username = None
                
                for reaction_key, reaction_data in self.reactions.items():
                    if possible_reaction1 in reaction_data["ar"]:
                        reaction_found = reaction_key
                        target_username = target_username1
                        break
                
                if not reaction_found:
                    for reaction_key, reaction_data in self.reactions.items():
                        if possible_reaction2 in reaction_data["ar"]:
                            reaction_found = reaction_key
                            target_username = target_username2
                            break
                
                if reaction_found and target_username:
                    await self.send_reactions(user, target_username, reaction_found)
                    return
            
            # نظام الرقصات
            # الأرقام = لوب دائماً
            # الأسماء = مرة واحدة (إلا إذا كتب "لوب")
            if len(parts) == 1:
                try:
                    dance_num = int(parts[0])
                    if 1 <= dance_num < len(self.emote_list):
                        await self.user_dance(user, dance_num, enable_loop=True)  # الأرقام دائماً مع لوب
                        return
                except (ValueError, IndexError):
                    pass
            
            # التحقق إذا الرسالة اسم رقصة (مرة واحدة فقط)
            if len(parts) == 1:
                for emote_key, emote in self.emotes.items():
                    # فحص الاسم الإنجليزي
                    if emote_key.lower() == msg_lower:
                        await self.user_dance(user, emote_key, enable_loop=False)
                        return
                    # فحص الأسماء العربية
                    for ar_name in emote.get("ar", []):
                        if ar_name.lower() == msg_lower:
                            await self.user_dance(user, emote_key, enable_loop=False)
                            return
            
            # التحقق إذا الرسالة اسم رقصة + "لوب"
            elif len(parts) == 2 and parts[1].lower() in ["لوب", "loop"]:
                loop_word = parts[0].lower()
                for emote_key, emote in self.emotes.items():
                    # فحص الاسم الإنجليزي
                    if emote_key.lower() == loop_word:
                        await self.user_dance(user, emote_key, enable_loop=True)
                        return
                    # فحص الأسماء العربية
                    for ar_name in emote.get("ar", []):
                        if ar_name.lower() == loop_word:
                            await self.user_dance(user, emote_key, enable_loop=True)
                            return
            
            # فحص الكلمات المحظورة
            if self.auto_mod:
                for word in self.banned_words:
                    if word.lower() in msg_lower:
                        await self.warn_user(user, "استخدام كلمات محظورة")
                        return
            
            # الحماية من السبام
            if self.spam_protection:
                if await self.check_spam(user):
                    await self.warn_user(user, "السبام")
                    return
            
            # معالجة الأوامر
            await self.handle_command(user, message)
            
        except Exception as e:
            print(f"Error in on_chat: {e}")
            import traceback
            traceback.print_exc()

    async def user_dance(self, user: User, dance_num, enable_loop: bool = False):
        """جعل المستخدم يرقص - مع نظام منع التداخل والتحقق من الرقصة"""
        try:
            # 1. منع ترقيص البوت من الآخرين
            if user.id == self.highrise.my_id:
                pass 

            # 2. نظام تتبع الطلبات لمنع التداخل عند السرعة
            import time
            request_id = time.time()
            self.active_dance_requests[user.id] = request_id

            # 3. إيقاف أي مهمة رقص سابقة
            if user.id in self.dancing_users:
                self.dancing_users[user.id].cancel()
                try:
                    del self.dancing_users[user.id]
                except: pass

            # 4. تحديد الرقصة (رقم أو اسم)
            emote = None
            if isinstance(dance_num, int):
                if 1 <= dance_num < len(self.emote_list):
                    emote = self.emote_list[dance_num]
            elif isinstance(dance_num, str):
                emote = self.emotes.get(dance_num)
            
            if not emote:
                 await self.highrise.send_whisper(user.id, f"❌ لم أجد هذه الرقصة: {dance_num}")
                 return

            # 5. تجهيز نص الرسالة
            dance_name_str = ""
            dance_number_str = ""
            
            # البحث عن الاسم العربي للرقصة
            for k, v in self.emotes.items():
                if v["id"] == emote["id"]:
                    dance_name_str = k
                    break
            
            if not dance_name_str:
                dance_name_str = dance_num if isinstance(dance_num, str) else "رقصة"

            # إيجاد رقم الرقصة من القائمة
            try:
                idx = self.emote_list.index(emote)
                dance_number_str = str(idx)
            except:
                dance_number_str = str(dance_num) if isinstance(dance_num, int) else "?"
            
            if enable_loop:
                msg = f"💃 رقصة: {dance_name_str} (رقم {dance_number_str}) - مستمر"
            else:
                msg = f"💃 رقصة رقم: {dance_number_str}"

            # 6. إرسال الرقصة (مع دعم البديل المجاني)
            await self.safe_send_emote(emote["id"], user.id)
            
            # 7. التأكد أن الطلب لا يزال صالحاً (لم يتم استبداله بطلب أسرع)
            if self.active_dance_requests.get(user.id) != request_id:
                return

            await self.highrise.send_whisper(user.id, msg)

            # 8. تشغيل اللوب إذا طلب المستخدم
            if enable_loop:
                task = asyncio.create_task(self.loop_dance(user.id, emote))
                self.dancing_users[user.id] = task
            
        except Exception as e:
            print(f"Error in user_dance: {e}")
            import traceback
            traceback.print_exc()
            try:
                await self.highrise.send_whisper(user.id, "❌ حدث خطأ بسيط في تشغيل الرقصة")
            except: pass
    
    async def dance_with_user(self, requester: User, target_username: str, dance_num):
        """
        الرقص الثنائي - أنت + يوزر ترقصوا نفس الرقصة مع لوب
        الصيغة: <رقم> <يوزر> أو <اسم_رقصة> <يوزر>
        """
        try:
            # ✅ منع ترقيص البوت
            target_user = await self.get_user_by_name(target_username)
            
            if not target_user:
                await self.highrise.send_whisper(requester.id, f"❌ لم يتم العثور على: {target_username}")
                return
            
            # ✅ منع ترقيص البوت
            bot_user_id = self.highrise.my_id
            if target_user.id == bot_user_id:
                await self.highrise.send_whisper(requester.id, "❌ ممنوع ترقيص البوت!")
                return
            
            # التأكد من وجود الرقصة
            emote = None
            
            # ✅ دعم الأرقام (عبر القائمة) والأسماء (عبر القاموس)
            if isinstance(dance_num, int):
                if 1 <= dance_num < len(self.emote_list):
                    emote = self.emote_list[dance_num]
            elif isinstance(dance_num, str):
                emote = self.emotes.get(dance_num)
                
            if not emote:
                await self.highrise.send_whisper(requester.id, f"❌ رقصة غير صحيحة!")
                return
            
            # ✨ حماية الملاك والمشرفين والمتميزين من الرقصات غير المرغوب فيها
            is_owner = target_user.username.lower() in [o.lower() for o in self.owners]
            is_target_admin = await self.is_admin(target_user)
            is_requester_admin = await self.is_admin(requester)
            is_distinguished = target_user.username.lower() in [u.lower() for u in self.distinguished_users]
            
            if is_owner and requester.id != target_user.id:
                await self.highrise.send_whisper(requester.id, "🛡️ لا يمكنك إجبار المالك على الرقص! الملوك يرقصون متى شاؤوا. 👑")
                return
            
            if is_target_admin and not is_requester_admin:
                await self.highrise.send_whisper(requester.id, "🛡️ لا يمكنك إجبار المشرف على الرقص! المشرفون يرقصون متى شاؤوا. 🛡️")
                return

            if is_distinguished:
                # التحقق إذا كان الشخص الذي يطلب الرقص ليس مشرفاً أو الطرف المتميز نفسه
                if not await self.is_admin(requester) and requester.id != target_user.id:
                    await self.highrise.send_whisper(requester.id, f"🛡️ @{target_user.username} شخص مميز، لا يمكنك إجباره على الرقص!")
                    return
            
            # إيقاف أي رقص سابق للطرفين
            if requester.id in self.dancing_users:
                self.dancing_users[requester.id].cancel()
                del self.dancing_users[requester.id]
            
            if target_user.id in self.dancing_users:
                self.dancing_users[target_user.id].cancel()
                del self.dancing_users[target_user.id]
            
            # إرسال نفس الرقصة للاثنين
            await asyncio.gather(
                self.highrise.send_emote(emote["id"], requester.id),
                self.highrise.send_emote(emote["id"], target_user.id)
            )
            
            # إنشاء لوب للاثنين
            task1 = asyncio.create_task(self.loop_dance(requester.id, emote))
            task2 = asyncio.create_task(self.loop_dance(target_user.id, emote))
            
            self.dancing_users[requester.id] = task1
            self.dancing_users[target_user.id] = task2
            
        except Exception as e:
            print(f"Error in dance_with_user: {e}")


    async def group_dance(self, admin: User, target_username: str, dance_num):
        """رقص جماعي - المشرف + اللاعب يرقصوا نفس الرقصة"""
        try:
            target_user = await self.get_user_by_name(target_username)
            if not target_user:
                await self.highrise.chat(f"❌ لم يتم العثور على: {target_username}")
                return
            
            emote = None
            
            # ✅ دعم الأرقام (عبر القائمة) والأسماء (عبر القاموس)
            if isinstance(dance_num, int):
                if 1 <= dance_num < len(self.emote_list):
                    emote = self.emote_list[dance_num]
            elif isinstance(dance_num, str):
                emote = self.emotes.get(dance_num)
            
            if not emote:
                await self.highrise.chat(f"❌ رقصة غير صحيحة!")
                return
            
            if admin.id in self.dancing_users:
                self.dancing_users[admin.id].cancel()
                del self.dancing_users[admin.id]
            
            if target_user.id in self.dancing_users:
                self.dancing_users[target_user.id].cancel()
                del self.dancing_users[target_user.id]
            
            await asyncio.gather(
                self.highrise.send_emote(emote["id"], admin.id),
                self.highrise.send_emote(emote["id"], target_user.id)
            )
            
            await self.highrise.chat(f"💃🕺 {admin.username} و {target_user.username} يرقصون رقصة {dance_num} معاً!")
            
            task1 = asyncio.create_task(self.loop_dance(admin.id, emote))
            task2 = asyncio.create_task(self.loop_dance(target_user.id, emote))
            self.dancing_users[admin.id] = task1
            self.dancing_users[target_user.id] = task2
            
        except Exception as e:
            print(f"Error in group_dance: {e}")
            await self.highrise.chat(f"❌ خطأ في الرقص الجماعي")
    
    async def stop_dance(self, user: User):
        """إيقاف رقص المستخدم وأي تفاعلات ثنائية"""
        try:
            # إلغاء الطلبات المعلقة
            if user.id in self.active_dance_requests:
                del self.active_dance_requests[user.id]
                
            if user.id in self.dancing_users:
                self.dancing_users[user.id].cancel()
                del self.dancing_users[user.id]
                print(f"Stopped dance task for {user.username}")
            

            
            try:
                await self.highrise.send_emote("idle-loop-happy", user.id)
                await asyncio.sleep(0.1)
                await self.highrise.send_emote("emote-no", user.id)
            except:
                await self.highrise.send_emote("emote-tired", user.id)
            
            await self.highrise.send_whisper(user.id, f"🛑 توقفت عن الرقص")
            
        except Exception as e:
            print(f"Error stopping dance: {e}")
    
    async def loop_dance(self, user_id: str, emote: dict):
        """تكرار الرقصة للأبد"""
        try:
            while True:
                if not self.connection_active:
                    break
                delay = max(emote["dur"], 3.0)
                await asyncio.sleep(delay)
                await self.safe_send_emote(emote["id"], user_id)
        except asyncio.CancelledError:
            print(f"Stopped dance loop for {user_id}")
        except Exception as e:
            print(f"Error in loop_dance: {e}")
    
    async def bot_auto_dance(self):
        """البوت يرقص تلقائياً - يتبدل بين جميع الرقصات المطلوبة"""
        dance_keys = ["floss", "swag", "ViralGroove", "PopularVibe", "Twerk", "Griddy", "TrueHeart"]
        current_idx = 0
        
        while self.bot_dancing and self.connection_active:
            try:
                if not self.connection_active:
                    break
                    
                key = dance_keys[current_idx]
                emote = self.emotes.get(key)
                if not emote:
                    # Fallback if key not found (shouldn't happen)
                    current_idx = (current_idx + 1) % len(dance_keys)
                    continue
                
                await self.highrise.send_emote(emote["id"])
                
                # وقت الرقصة + قليل من التأخير
                delay = max(emote["dur"] + 0.5, 5.0)
                await asyncio.sleep(delay)
                
                # الانتقال للرقصة التالية
                current_idx = (current_idx + 1) % len(dance_keys)
                
            except asyncio.CancelledError:
                print("Bot auto-dance stopped")
                break
            except Exception as e:
                error_msg = str(e)
                if "transport" in error_msg.lower() or "closing" in error_msg.lower():
                    print("Connection lost detected. Stopping dance task.")
                    self.connection_active = False
                    break
                if "User not in room" not in error_msg:
                    print(f"Error in bot auto-dance: {e}")
                await asyncio.sleep(5)
    
    async def safe_send_emote(self, emote_id, user_id, fallback_id="emote-tired"):
        """محاولة إرسال رقصة، وإذا فشلت (لعدم الملكية) نرسل رقصة بديلة مجانية"""
        try:
            await self.highrise.send_emote(emote_id, user_id)
        except Exception as e:
            # إذا فشل بسبب عدم الملكية، نرسل البديل
            if "owned" in str(e) or "free" in str(e):
                try:
                    await self.highrise.send_emote(fallback_id, user_id)
                except:
                    pass
            else:
                print(f"Error sending emote {emote_id}: {e}")

    async def perform_interaction(self, user: User, target_username: str, interaction: dict, is_loop: bool = False):
        """تنفيذ تفاعل بين مستخدمين (فاعل ومفعول به)"""
        try:
            target_user = await self.get_user_by_name(target_username)
            if not target_user:
                await self.highrise.send_whisper(user.id, f"❌ لم يتم العثور على: {target_username}")
                return
            
            # منع التفاعل مع البوت (بشكل عام)
            if target_user.id == self.highrise.my_id:
                await self.highrise.send_whisper(user.id, "❌ لا يمكنك فعل ذلك مع البوت!")
                return
            
            # ✨ حماية الملاك والمشرفين والمتميزين من التفاعلات
            is_owner = target_user.username.lower() in [o.lower() for o in self.owners]
            is_target_admin = await self.is_admin(target_user)
            is_requester_admin = await self.is_admin(user)
            is_distinguished = target_user.username.lower() in [u.lower() for u in self.distinguished_users]
            
            # تحديد التفاعلات "غير الجميلة"
            bad_interactions = ["slap", "punch", "kick", "stab", "shoot", "bite", "scare", "laugh"]
            
            if is_owner and user.id != target_user.id:
                await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك استخدام التفاعلات مع الملاك! لديهم حصانة كاملة. 👑")
                return
            
            if is_target_admin and not is_requester_admin:
                await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك استخدام التفاعلات مع المشرفين! لديهم حصانة ضد اللاعبين العاديين. 🛡️")
                return

            if is_distinguished:
                # التحقق إذا كان التفاعل في القائمة السوداء
                interaction_key = next((k for k, v in self.interactions.items() if v == interaction), "unknown")
                if interaction_key in bad_interactions:
                    await self.highrise.send_whisper(user.id, f"🛡️ هذا الشخص مميز! لا يمكنك استخدام رقصات مخلة أو تفاعلات مزعجة معه.")
                    return
            
            # إيقاف أي رقص سابق للطرفين إذا كان لوب
            if is_loop:
                if user.id in self.dancing_users:
                    self.dancing_users[user.id].cancel()
                if target_user.id in self.dancing_users:
                    self.dancing_users[target_user.id].cancel()
                
                await self.highrise.chat(f"🔥 {user.username} بدأ سلسلة {interaction['ar'][0]} على {target_user.username}!")
                
                task = asyncio.create_task(self.loop_interaction(user.id, target_user.id, interaction))
                self.dancing_users[user.id] = task
                
            else:
                # محاولة تنفيذ التفاعل مرة واحدة مع استخدام البديل الآمن
                await asyncio.gather(
                    self.safe_send_emote(interaction["id"], user.id, "emoji-angry"),
                    self.safe_send_emote(interaction["target_id"], target_user.id, "emote-tired")
                )
                await self.highrise.chat(f"🔥 {user.username} قام بـ {interaction['ar'][0]} {target_user.username}!")
            
        except Exception as e:
            print(f"Error in perform_interaction: {e}")

    async def loop_interaction(self, user_id: str, target_id: str, interaction: dict):
        """لوب التفاعل"""
        try:
            while True:
                if not self.connection_active:
                    break
                await asyncio.gather(
                    self.safe_send_emote(interaction["id"], user_id, "emoji-angry"),
                    self.safe_send_emote(interaction["target_id"], target_id, "emote-tired")
                )
                delay = max(interaction["dur"] + 0.5, 3.0)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in loop_interaction: {e}")

    async def send_reactions(self, user: User, target_username: str, reaction_type: str):
        """Bot sends real reactions to target user"""
        print(f"send_reactions: {user.username} -> {target_username} ({reaction_type})")
        
        target_user = await self.get_user_by_name(target_username)
        if not target_user:
            await self.highrise.chat(f"❌ لم يتم العثور على المستخدم: {target_username}")
            return
        
        # ✅ منع إرسال رياكشنات للبوت والملاك والمشرفين
        bot_user_id = self.highrise.my_id
        is_owner = target_user.username.lower() in [o.lower() for o in self.owners]
        is_target_admin = await self.is_admin(target_user)
        is_requester_admin = await self.is_admin(user)
        
        if target_user.id == bot_user_id:
            await self.highrise.send_whisper(user.id, "❌ ممنوع إرسال رياكشنات للبوت!")
            return
        
        if is_owner and user.id != target_user.id:
            await self.highrise.send_whisper(user.id, "🛡️ الملاك لديهم حصانة ضد الرياكشنات المزعجة! 👑")
            return
            
        if is_target_admin and not is_requester_admin:
            await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك إرسال رياكشنات مزعجة للمشرفين! 🛡️")
            return
        
        reaction_map = {
            "heart": {"reaction": "heart", "ar": ["قلب", "ق", "حب", "ح", "h"]},
            "thumbs": {"reaction": "thumbs", "ar": ["اعجاب", "ا", "لايك", "ثامز", "thumbs"]},
            "clap": {"reaction": "clap", "ar": ["تصفيق", "ت", "كلاب", "clap"]},
            "wave": {"reaction": "wave", "ar": ["تلويح", "تل", "باي", "wave"]},
            "wink": {"reaction": "wink", "ar": ["غمزة", "غ", "وينك", "wink"]},
        }
        
        reaction_name = None
        reaction_value = None
        
        for key, data in reaction_map.items():
            if reaction_type.lower() == key.lower() or reaction_type.lower() in data["ar"]:
                reaction_name = key
                reaction_value = data["reaction"]
                break
        
        if not reaction_value:
            reactions_list = "، ".join([f"{k}: {'/'.join(v['ar'])}" for k, v in reaction_map.items()])
            await self.highrise.chat(f"❌ رياكشن غير صحيح!\n💝 الرياكشنات المتاحة:\n{reactions_list}")
            return
        
        try:
            # ✅ إرسال 50 رياكشن دفعة واحدة
            total_to_send = 50
            
            await self.highrise.chat(f"💝 جاري إرسال 50 {reaction_name} لـ {target_user.username}...")
            
            # إنشاء كل المهام دفعة واحدة
            tasks = []
            for _ in range(total_to_send):
                tasks.append(asyncio.create_task(self.highrise.react(reaction_value, target_user.id)))
            
            # تنفيذها كلها في نفس الوقت
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await self.highrise.chat(f"✅ تم إرسال 50 {reaction_name} بنجاح!")
            
        except Exception as e:
            print(f"Error in reactions: {e}")

    async def handle_command(self, user: User, message: str):
        """معالجة أوامر البوت - مُصلحة بالكامل"""
        if message.startswith("!"):
            message = message[1:]
        
        parts = message.split()
        if not parts:
            return
            
        command = parts[0].lower()
        is_admin_user = await self.is_admin(user)
        
        if command in ["help", "مساعدة", "مساعده", "هيلب", "الاوامر", "الأوامر", "اوامر"]:
            help_message = "🌑 مجلس روم بلاك:\n✨ help: مساعدة\n🏢 floors: الطوابق\n💎 vip: للمشايخ\n🎮 game: ألعاب\n🕺 emotes: رقصات\n☕ إدارة: كتم/طرد/إعلان/مسح"
            await self.safe_whisper(user.id, help_message)
            return
        
        elif command in ["users", "مستخدمين", "يوزرز", "الاعبين", "اللاعبين", "ناس"]:
            await self.list_users()
            return
        
        elif command in ["time", "وقت", "الوقت", "تايم", "ساعة", "الساعة", "كم", "الساعه"]:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            await self.highrise.chat(f"⏰ الوقت الحالي: {current_time}")
            return
        
        elif command in ["bot", "بوت", "روبوت"]:
            await self.highrise.chat("🤖 أنا بوت إدارة الغرفة! استخدم: مساعدة")
            return
        
        elif command in ["رقصات", "الرقصات", "emotes", "رقص"]:
            emotes_help = """🕺 كيف ترقص؟
1. اكتب رقم رقصة (1-239)
2. اكتب: اسم_الرقصة (مثلاً: شافل)
3. اكتب: اسم_الرقصة لوب (للتكرار)
✨ رقصات مشهورة:
شافل، داب، تويرك، قيتار، انمي، بطل، زومبي
🛑 لإيقاف الرقص اكتب: 0"""
            await self.safe_whisper(user.id, emotes_help)
            return

        elif command in ["game", "games", "ألعاب", "العاب", "لعبة", "لعبه"]:
            games_msg = """🎮 الألعاب المتاحة قريباً:
1️⃣ لعبة الأسئلة (قريباً)
2️⃣ لعبة الجولد (قريباً)
✨ حالياً يمكنك استخدام: رقصني (ليختار البوت لك رقصة عشوائية)"""
            await self.safe_whisper(user.id, games_msg)
            return

        elif command in ["رقصني", "dance_me", "ارقص_لي"]:
             # اختيار رقصة عشوائية مع لوب
             try:
                 random_dance = random.randint(1, len(self.emote_list) - 1)
                 await self.user_dance(user, random_dance, enable_loop=True)
             except:
                 pass
             return
        

        
        # ═══════════════════════════════════════
        # 🏢 أوامر التنقل (للجميع - بدون اسم يوزر)
        # ═══════════════════════════════════════
        
        elif command in ["ارضي", "ground", "ارضيه", "الارضي", "تحت", "down"] and len(parts) == 1:
            try:
                await self.highrise.teleport(user.id, self.floors["ground"])
                self.user_floors[user.id] = "ground"
                await self.highrise.send_whisper(user.id, f"🏢 انتقلت للطابق الأرضي")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ خطأ: {e}")
            return
        
        elif (command in ["first", "up1", "الاول", "طابق_اول", "اول", "فوق"] and len(parts) == 1) or \
             (command in ["فوق", "up"] and len(parts) == 2 and parts[1] == "1"):
            try:
                await self.highrise.teleport(user.id, self.floors["floor1"])
                self.user_floors[user.id] = "floor1"
                await self.highrise.send_whisper(user.id, f"🏬 انتقلت إلى (فوق)")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ خطأ: {e}")
            return

        elif (command in ["second", "up2", "الثاني", "طابق_ثاني", "ثاني", "فوق2"] and len(parts) == 1) or \
             (command in ["فوق2", "up"] and len(parts) == 2 and parts[1] == "2"):
            try:
                await self.highrise.teleport(user.id, self.floors["floor2"])
                self.user_floors[user.id] = "floor2"
                await self.highrise.send_whisper(user.id, f"🏬 انتقلت إلى (فوق2)")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ خطأ: {e}")
            return
        
        elif (command in ["vip", "شخصية_مهمة", "في_اي_بي"] and len(parts) == 1):
            is_admin = await self.is_admin(user)
            if not is_admin:
                await self.highrise.send_whisper(user.id, "❌ طابق VIP مخصص للمشرفين فقط!")
                return
            try:
                await self.highrise.teleport(user.id, self.floors["vip"])
                self.user_floors[user.id] = "vip"
                await self.highrise.send_whisper(user.id, f"💎 انتقلت إلى طابق VIP")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ خطأ: {e}")
            return
        
        elif command in ["طوابق", "floors", "الطوابق", "اين", "وين"]:
            floors_info = """
🏢 الطوابق المتاحة:

🏢 الأرضي: ارضي / ground
🏬 فوق: فوق / first
🏬 فوق2: فوق2 / second
💎 VIP: vip (للمشايخ فقط)

✨ انقر على أي نقطة في طابق آخر
   وسينقلك بالضبط للمكان! 🎯
"""
            await self.highrise.send_whisper(user.id, floors_info)
            return
        
        if not is_admin_user:
            # رسالة للمستخدمين العاديين إذا حاولوا استخدام أمر مشرف
            admin_commands = ["طرد", "حظر", "كتم", "kick", "ban", "mute", "تحذير", "warn",
                            "جلب", "tphere", "come", "جيب", "هات", "سحب", "br", "روح", "tpto", "رح", "تجميد", "freeze", "جمد", "قل", "say",
                            "نقل_الكل", "r", "ر", "تحت", "down", "فوق", "up", "vip", "إعلان", "اعلان", "أعلن", "مسح", "تنظيف",
                            "addmod", "اضف_مشرف", "removemod", "ازالة_مشرف", "ازل_مشرف", "invite", "دعوة", "tip", "جولد",
                            "switch", "تبديل", "بدل", "move", "نقل_موقع", "equip", "ارتدي", "لبس",
                            "addvip", "اضف_vip", "اضافة_vip", "removevip", "ازالة_vip", "adddist", "تميز", "تمييز"]
            
            if command in admin_commands:
                await self.highrise.send_whisper(user.id, "❌ مسموح فقط للمشرفين (المشايخ) باستخدام هذا الأمر")
            return
        
        # ═══════════════════════════════════════
        # 👑 أوامر المشرفين (بعد التحقق)
        # ═══════════════════════════════════════
        
        # 💃 الرقص الجماعي: <رقم> <يوزر>
        if len(parts) == 2:
            try:
                dance_num = int(parts[0])
                if 1 <= dance_num < len(self.emote_list):
                    await self.group_dance(user, parts[1], dance_num)
                    return
            except ValueError:
                first_word = parts[0].lower()
                for emote_key, emote in self.emotes.items():
                    if emote_key.lower() == first_word:
                        await self.group_dance(user, parts[1], emote_key)
                        return
                    for ar_name in emote.get("ar", []):
                        if ar_name.lower() == first_word:
                            await self.group_dance(user, parts[1], emote_key)
                            return
        
        if command in ["r", "ر", "قلوب", "قلوب_للكل"]:
            try:
                room_users = await self.highrise.get_room_users()
                total_users = len(getattr(room_users, 'content', []))
                
                await self.highrise.chat(f"💝 البوت يرسل قلوب لكل اللاعبين ({total_users} لاعب)...")
                
                # إرسال على دفعات لتجنب فصل الاتصال
                success_count = 0
                for player, _ in getattr(room_users, 'content', []):
                    try:
                        await self.highrise.react("heart", player.id)
                        success_count += 1
                        await asyncio.sleep(0.3)
                    except Exception:
                        pass
                
                await self.highrise.chat(f"✅ تم إرسال {success_count} قلب لـ {total_users} لاعب! 💝💝")
                
            except Exception as e:
                print(f"Error in bulk hearts: {e}")
                await self.highrise.chat(f"❌ حدث خطأ")
            return
        
        # أوامر نقل اللاعبين
        elif command in ["تحت", "down"] and len(parts) >= 2:
            target_user = await self.get_user_by_name(parts[1])
            if target_user:
                if target_user.id == self.highrise.my_id:
                     await self.highrise.chat("❌ لا يمكنني نقل نفسي!")
                     return
                
                # حماية الملاك والمشرفين
                if self.is_owner(target_user) or await self.is_admin(target_user):
                    if not self.is_owner(user):
                        await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك نقل الملاك أو المشرفين!")
                        return

                await self.highrise.teleport(target_user.id, self.floors["ground"])
                self.user_floors[target_user.id] = "ground"
                await self.highrise.chat(f"⬇️ تم نقل {parts[1]} تحت")
            else:
                await self.highrise.chat(f"❌ لم يتم العثور على: {parts[1]}")
            return
        
        elif command in ["فوق", "up"] and len(parts) >= 2:
            target_user = await self.get_user_by_name(parts[1])
            if target_user:
                if target_user.id == self.highrise.my_id:
                     await self.highrise.chat("❌ لا يمكنني نقل نفسي!")
                     return
                
                # حماية الملاك والمشرفين
                if self.is_owner(target_user) or await self.is_admin(target_user):
                    if not self.is_owner(user):
                        await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك نقل الملاك أو المشرفين!")
                        return

                await self.highrise.teleport(target_user.id, self.floors["floor1"])
                self.user_floors[target_user.id] = "floor1"
                await self.highrise.chat(f"⬆️ تم نقل {parts[1]} فوق")
            else:
                await self.highrise.chat(f"❌ لم يتم العثور على: {parts[1]}")
            return
        
        elif command in ["vip", "في_اي_بي"] and len(parts) >= 2:
            target_user = await self.get_user_by_name(parts[1])
            if target_user:
                if target_user.id == self.highrise.my_id:
                     await self.highrise.chat("❌ لا يمكنني نقل نفسي!")
                     return
                
                # حماية الملاك والمشرفين
                if self.is_owner(target_user) or await self.is_admin(target_user):
                    if not self.is_owner(user):
                        await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك نقل الملاك أو المشرفين!")
                        return

                await self.highrise.teleport(target_user.id, self.floors["vip"])
                self.user_floors[target_user.id] = "vip"
                await self.highrise.chat(f"💎 تم نقل {parts[1]} إلى طابق VIP")
            else:
                await self.highrise.chat(f"❌ لم يتم العثور على: {parts[1]}")
            return
        
        # أوامر المالك
        elif command in ["addmod", "addadmin", "اضف_مشرف", "اضف_ادمن"]:
            if user.username.lower() not in [o.lower() for o in self.owners]:
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر للملاك فقط!")
                return
            if len(parts) >= 2:
                new_admin = parts[1]
                # إزالة علامة @ إذا كتبها المالك
                if new_admin.startswith("@"):
                    new_admin = new_admin[1:]
                if new_admin.lower() not in [a.lower() for a in self.admins]:
                    self.admins.append(new_admin)
                    self.save_config()
                    await self.highrise.chat(f"✅ تم إضافة @{new_admin} كمشرف")
                else:
                    await self.highrise.send_whisper(user.id, "❌ هذا المستخدم مشرف بالفعل")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: اضف_مشرف أحمد")
            return
        
        elif command in ["removemod", "removeadmin", "ازالة_مشرف", "ازل_مشرف", "ازالة_ادمن"]:
            if user.username.lower() not in [o.lower() for o in self.owners]:
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر للملاك فقط!")
                return
            if len(parts) >= 2:
                old_admin = parts[1].lower()
                if old_admin.startswith("@"):
                    old_admin = old_admin[1:]
                original_admin = next((a for a in self.admins if a.lower() == old_admin), None)
                if original_admin:
                    self.admins.remove(original_admin)
                    self.save_config()
                    await self.highrise.chat(f"✅ تم إزالة إشراف @{parts[1].replace('@', '')}")
                else:
                    await self.highrise.send_whisper(user.id, "❌ هذا المستخدم ليس مشرفاً")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: ازالة_مشرف أحمد")
            return
        # باقي أوامر المشرفين
        elif command in ["طرد", "kick"]:
            if not is_admin_user: return
            if len(parts) >= 2:
                # محاولة طرد اللاعب وحمايته إذا كان مالكاً
                await self.kick_user(parts[1], user)
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: طرد أحمد")
            return

        elif command in ["إعلان", "اعلان", "أعلن", "announcement"]:
            if not is_admin_user: return
            if len(parts) > 1:
                msg = " ".join(parts[1:])
                await self.highrise.chat("📢 إعــــلان هــــام 📢")
                await self.highrise.chat(f"✨ {msg} ✨")
            else:
                await self.safe_whisper(user.id, "❌ مثال: اعلان القهوة جاهزة يا شباب")
            return

        elif command in ["مسح", "clear", "تنظيف"]:
            if not is_admin_user: return
            # تنظيف الشات عبر إرسال رسائل فارغة كثيرة (أسلوب تقني)
            await self.highrise.chat("🧹 جاري تنظيف المجلس...")
            for _ in range(15):
                await self.highrise.chat("ㅤ") # حرف مخفي
            await self.highrise.chat("✅ تم تنظيف الشات بنجاح!")
            return
        
        elif command in ["ban", "حظر", "احظر", "بان"]:
            if len(parts) >= 2:
                duration = int(parts[2]) if len(parts) >= 3 else 3600
                await self.ban_user(parts[1], duration)
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: حظر أحمد")
            return
        
        elif command in ["unban", "فك_حظر", "فك"]:
            if len(parts) >= 2:
                await self.unban_user(parts[1])
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: فك أحمد")
            return
        
        elif command in ["mute", "كتم", "اكتم", "ميوت"]:
            if len(parts) >= 2:
                duration = int(parts[2]) if len(parts) >= 3 else 600
                await self.mute_user(parts[1], duration)
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: كتم أحمد")
            return
        
        elif command in ["unmute", "فك_كتم", "فك_الكتم"]:
            if len(parts) >= 2:
                await self.unmute_user(parts[1])
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: فك_كتم أحمد")
            return
        
        elif command in ["warn", "تحذير", "حذر", "انذار"]:
            if len(parts) >= 2:
                reason = " ".join(parts[2:]) if len(parts) > 2 else "مخالفة قوانين الغرفة"
                target = await self.get_user_by_name(parts[1])
                if target:
                    await self.warn_user(target, reason)
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: تحذير أحمد")
            return
        
        elif command in ["tphere", "come", "جيب", "هات", "سحب", "br"]:
            if len(parts) >= 2:
                target_user = await self.get_user_by_name(parts[1])
                if target_user:
                    if target_user.id == user.id: return
                    
                    # حماية الملاك والمشرفين
                    if self.is_owner(target_user) or await self.is_admin(target_user):
                        if not self.is_owner(user):
                            await self.highrise.send_whisper(user.id, "🛡️ لا يمكنك جلب الملاك أو المشرفين!")
                            return

                    room_users = await self.highrise.get_room_users()
                    for u, pos in getattr(room_users, 'content', []):
                        if u.id == user.id:
                            await self.highrise.teleport(target_user.id, pos)
                            self.user_floors[target_user.id] = self._get_floor_name(pos.y) or "ground"
                            await self.highrise.chat(f"✅ تم جلب {parts[1]}")
                            break
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: جلب أحمد")
            return
        
        elif command in ["tpto", "روح", "رح", "روح_لـ"]:
            if len(parts) >= 2:
                target_user = await self.get_user_by_name(parts[1])
                if target_user:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in getattr(room_users, 'content', []):
                        if u.id == target_user.id:
                            await self.highrise.teleport(user.id, pos)
                            await self.highrise.chat(f"✅ انتقل المشرف إلى {parts[1]}")
                            break
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: روح أحمد")
            return
        
        elif command in ["freeze", "تجميد", "جمد", "فريز", "تثبيت", "وقف", "ثبت"]:

            if len(parts) >= 2:
                await self.freeze_user(parts[1])
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: تجميد أحمد")
            return
        
        elif command in ["unfreeze", "فك_تجميد", "فك_التجميد", "حرر", "فك"]:
            if len(parts) >= 2:
                await self.unfreeze_user(parts[1])
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: فك_تجميد أحمد")
            return

        # ═══════════════════════════════════════
        # 💰 توزيع الجولد
        # ═══════════════════════════════════════
        elif command in ["tip", "جولد", "اعطي"]:
            await self.tip_user(user, parts)
            return

        # ═══════════════════════════════════════
        # 📨 الدعوات
        # ═══════════════════════════════════════
        elif command in ["invite", "دعوة", "دعوه"]:
            custom_msg = " ".join(parts[1:]) if len(parts) > 1 else ""
            await self.send_invites(user, custom_msg)
            return

        # ═══════════════════════════════════════
        # 👗 نسخ ملابس مستخدم
        # ═══════════════════════════════════════
        elif command in ["equip", "ارتدي", "لبس"]:
            if len(parts) >= 2:
                await self.equip_bot_from_user(user, parts[1])
            else:
                await self.safe_whisper(user.id, "❌ مثال: equip اسم_البوت")
            return

        # ═══════════════════════════════════════
        # 🔄 تبديل المواقع
        # ═══════════════════════════════════════
        elif command in ["switch", "تبديل", "بدل"]:
            if len(parts) >= 2:
                await self.switch_positions(user, parts[1])
            else:
                await self.safe_whisper(user.id, "❌ مثال: switch اسم")
            return

        elif command in ["move", "نقل_موقع"]:
            if len(parts) >= 3:
                await self.move_users(user, parts[1], parts[2])
            else:
                await self.safe_whisper(user.id, "❌ مثال: move اسم1 اسم2")
            return

        # ═══════════════════════════════════════
        # ⭐ إدارة VIP
        # ═══════════════════════════════════════
        elif command in ["addvip", "اضف_vip", "اضافة_vip"]:
            if len(parts) >= 2:
                new_vip = parts[1].replace("@", "")
                if new_vip.lower() not in [v.lower() for v in self.vip_users]:
                    self.vip_users.append(new_vip)
                    self.save_config()
                    await self.safe_chat(f"⭐ تم إضافة @{new_vip} لقائمة VIP")
                else:
                    await self.safe_whisper(user.id, "❌ هذا المستخدم في قائمة VIP بالفعل")
            else:
                await self.safe_whisper(user.id, "❌ مثال: addvip اسم")
            return

        elif command in ["removevip", "ازالة_vip", "حذف_vip"]:
            if len(parts) >= 2:
                old_vip = parts[1].replace("@", "").lower()
                original = next((v for v in self.vip_users if v.lower() == old_vip), None)
                if original:
                    self.vip_users.remove(original)
                    self.save_config()
                    await self.safe_chat(f"⭐ تم إزالة @{original} من قائمة VIP")
                else:
                    await self.safe_whisper(user.id, "❌ هذا المستخدم ليس في قائمة VIP")
            else:
                await self.safe_whisper(user.id, "❌ مثال: removevip اسم")
            return

        elif command == "vip" and len(parts) >= 2 and parts[1].lower() in ["list", "قائمة"]:
            if self.vip_users:
                vip_list = "\n".join([f"⭐ @{v}" for v in self.vip_users])
                await self.safe_whisper(user.id, f"⭐ قائمة VIP:\n{vip_list}")
            else:
                await self.safe_whisper(user.id, "❌ قائمة VIP فارغة")
            return

        elif command in ["adddist", "تميز", "تمييز", "اضف_مميز"]:
            if not is_admin_user: return
            if len(parts) >= 2:
                new_dist = parts[1].replace("@", "")
                if new_dist.lower() not in [u.lower() for u in self.distinguished_users]:
                    self.distinguished_users.append(new_dist)
                    self.save_config()
                    await self.safe_chat(f"✨ تم إضافة @{new_dist} لقائمة التميز (محمي من التفاعلات المزعجة) 🛡️")
                else:
                    await self.safe_whisper(user.id, "❌ هذا المستخدم مميز بالفعل")
            else:
                await self.safe_whisper(user.id, "❌ مثال: تميز أحمد")
            return

        elif command in ["removedist", "الغاء_تميز", "حذف_مميز"]:
            if not is_admin_user: return
            if len(parts) >= 2:
                old_dist = parts[1].replace("@", "").lower()
                original = next((u for u in self.distinguished_users if u.lower() == old_dist), None)
                if original:
                    self.distinguished_users.remove(original)
                    self.save_config()
                    await self.safe_chat(f"🛡️ تم إزالة @{original} من قائمة التميز")
                else:
                    await self.safe_whisper(user.id, "❌ هذا المستخدم ليس في قائمة التميز")
            else:
                await self.safe_whisper(user.id, "❌ مثال: الغاء_تميز أحمد")
            return

        elif command in ["distlist", "قائمة_التميز"]:
            if self.distinguished_users:
                dist_list = "\n".join([f"✨ @{u}" for u in self.distinguished_users])
                await self.safe_whisper(user.id, f"📝 قائمة المستخدمين المميزين:\n{dist_list}")
            else:
                await self.safe_whisper(user.id, "❌ لا يوجد مميزين")
            return
        elif command == "admin" and len(parts) >= 2 and parts[1].lower() in ["list", "قائمة"]:
            if self.admins:
                valid_admins = [a for a in self.admins if a]
                if valid_admins:
                    admins_str = ", ".join([f"🛡️ @{a}" for a in valid_admins])
                    await self.safe_whisper(user.id, f"🛡️ قائمة المشرفين:\n{admins_str}")
                else:
                    await self.highrise.chat("لا يوجد مشرفين حالياً")
            return

        elif command in ["نقل_الكل", "teleport_all"]:
            if len(parts) >= 2:
                floor_name = parts[1].lower()
                
                if floor_name in ["arضي", "ground", "0"]:
                    target_floor = self.floors["ground"]
                    floor_text = "الطابق الأرضي 🏢"
                elif floor_name in ["اول", "first", "1"]:
                    target_floor = self.floors["floor1"]
                    floor_text = "الطابق الأول 🏬"
                elif floor_name in ["ثاني", "second", "2"]:
                    target_floor = self.floors["floor2"]
                    floor_text = "الطابق الثاني 🏬"
                elif floor_name in ["vip", "في_اي_بي", "v"]:
                    target_floor = self.floors["vip"]
                    floor_text = "طابق VIP 💎"
                else:
                    await self.highrise.send_whisper(user.id, "❌ طابق غير صحيح")
                    return
                
                try:
                    room_users = await self.highrise.get_room_users()
                    count = 0
                    for u, _ in getattr(room_users, 'content', []):
                        if u.id != user.id:
                            # حماية الملاك والمشرفين والمميزين من النقل الجماعي
                            is_target_protected = self.is_owner(u) or u.username.lower() in [a.lower() for a in self.admins if a] or u.username.lower() in [d.lower() for d in self.distinguished_users]
                            if is_target_protected: continue
                            
                            await self.highrise.teleport(u.id, target_floor)
                            count += 1
                    
                    await self.highrise.chat(f"✅ تم نقل {count} مستخدم إلى {floor_text}")
                except Exception as e:
                    await self.highrise.chat(f"❌ خطأ: {e}")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: نقل_الكل ارضي")
            return
        
        elif command in ["ترحيب", "welcome"]:
            if len(parts) >= 2:
                self.welcome_message = " ".join(parts[1:])
                self.save_config()
                welcome_type = "عامة 📢" if self.welcome_public else "همس 💬"
                await self.highrise.chat(f"✅ تم تحديث رسالة الترحيب ({welcome_type})")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: ترحيب أهلا بك في المجلس")
            return
        
        elif command in ["welcometype", "نوع_الترحيب"]:
            self.welcome_public = not self.welcome_public
            self.save_config()
            welcome_type = "عامة 📢" if self.welcome_public else "همس 💬"
            await self.highrise.chat(f"✅ الترحيب الآن عبر الـ: {welcome_type}")
            return
        
        elif command in ["ترحيب_خاص", "customwelcome", "vip_welcome"]:
            if len(parts) >= 3:
                target_name = parts[1]
                if target_name.startswith("@"):
                    target_name = target_name[1:]
                
                custom_msg = " ".join(parts[2:])
                self.custom_welcomes[target_name.lower()] = custom_msg
                self.save_config()
                
                await self.highrise.chat(f"✅ تم تعيين ترحيب خاص لـ @{target_name}")
                await self.highrise.send_whisper(user.id, f"📝 الرسالة: {custom_msg}")
            elif len(parts) == 2 and parts[1].lower() in ["قائمة", "list"]:
                if self.custom_welcomes:
                    msg = "📋 الترحيبات الخاصة:\n"
                    for name, wmsg in self.custom_welcomes.items():
                        msg += f"• @{name}: {wmsg}\n"
                    await self.highrise.send_whisper(user.id, msg)
                else:
                    await self.highrise.send_whisper(user.id, "❌ لا توجد ترحيبات خاصة")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: ترحيب_خاص @الاسم رسالة الترحيب")
            return
        
        elif command in ["حذف_ترحيب", "removewelcome"]:
            if len(parts) >= 2:
                target_name = parts[1].lower()
                if target_name.startswith("@"):
                    target_name = target_name[1:]
                if target_name in self.custom_welcomes:
                    del self.custom_welcomes[target_name]
                    self.save_config()
                    await self.highrise.chat(f"✅ تم حذف الترحيب الخاص لـ @{target_name}")
                else:
                    await self.highrise.send_whisper(user.id, f"❌ لا يوجد ترحيب خاص لـ @{target_name}")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: حذف_ترحيب @الاسم")
            return

        elif command in ["wallet", "محفظة", "فلوس", "رصيد"]:
            # التحقق من رصيد البوت
            if not self.is_owner(user):
                await self.highrise.send_whisper(user.id, "❌ هذا الأمر للملاك فقط!")
                return
            try:
                res_wallet = await self.highrise.get_wallet()
                if hasattr(res_wallet, 'content'):
                    msg = "💰 رصيد البوت الحالي:"
                    found_currencies = False
                    for currency in res_wallet.content:
                        # تحويل أسماء العملات للعربية للتسهيل
                        c_type = currency.type
                        if c_type == "gold": c_type = "ذهب"
                        elif c_type == "bubbles": c_type = "فقاعات (Bubbles)"
                        
                        msg += f"\n- {c_type}: {currency.amount}"
                        found_currencies = True
                    
                    if not found_currencies:
                        msg += "\n(المحفظة فارغة 0)"
                        
                    await self.highrise.chat(msg)
                else:
                    await self.highrise.chat(f"❌ خطأ في جلب الرصيد: {res_wallet}")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
            return
        


        # استعراض المشرفين (للجميع)
        elif command in ["admins", "مشرفين", "المشرفين", "الادمنية"]:
            if self.admins:
                valid_admins = [a for a in self.admins if a]
                if valid_admins:
                    admins_str = ", ".join([f"@{a}" for a in valid_admins])
                    await self.highrise.chat(f"🛡️ مشرفو المجلس: {admins_str}")
                else:
                    await self.highrise.chat("لا يوجد مشرفين حالياً")
            else:
                await self.highrise.chat("لا يوجد مشرفين حالياً")
            return
        
        elif command in ["find", "بحث"]:
            if len(parts) >= 2:
                search_name = parts[1]
                user_found = await self.get_user_by_name(search_name)
                if user_found:
                    await self.highrise.chat(f"✅ وجدت المستخدم:\n📝 الاسم: @{user_found.username}\n🆔 المعرف: {user_found.id}")
                else:
                    await self.highrise.chat(f"❌ لم أجد مستخدم باسم: {search_name}")
            else:
                await self.highrise.send_whisper(user.id, "❌ مثال: بحث أحمد")
            return
        
        elif command in ["احداثيات", "موقعي", "pos", "position", "coords"]:
            try:
                room_users = await self.highrise.get_room_users()
                for u, pos in getattr(room_users, 'content', []):
                    if u.id == user.id:
                        position_info = f"""
📍 إحداثياتك:
━━━━━━━━━━━━━━━
X: {pos.x}
Y: {pos.y}
Z: {pos.z}
Facing: {pos.facing}
━━━━━━━━━━━━━━━
📋 للنسخ:
Position({pos.x}, {pos.y}, {pos.z}, "{pos.facing}")
"""
                        await self.highrise.send_whisper(user.id, position_info)
                        return
                await self.highrise.send_whisper(user.id, "❌ لم أتمكن من إيجاد موقعك")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ خطأ: {e}")
            return
        
        # أوامر المالك فقط
        if self.is_owner(user):
            if command in ["هنا", "setbot", "set_bot"]:
                try:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in getattr(room_users, 'content', []):
                        if u.id == user.id:
                            self.bot_position = pos
                            self.save_config()
                            # Teleport bot to the new location immediately
                            await self.highrise.teleport(self.highrise.my_id, self.bot_position)
                            await self.highrise.chat(f"📍 تم تحديد موقع البوت الجديد هنا @{user.username} وتم نقله!")
                            return
                    await self.highrise.send_whisper(user.id, "❌ لم أتمكن من العثور على موقعك لتحديد مكان البوت")
                except Exception as e:
                    print(f"Error in setbot command: {e}")
                    await self.highrise.send_whisper(user.id, f"❌ خطأ: {e}")
                return
            
            if command in ["addowner", "اضافة_مالك"]:
                if len(parts) >= 2:
                    new_owner = parts[1]
                    if new_owner.startswith("@"):
                        new_owner = new_owner[1:]
                    if new_owner.lower() not in [o.lower() for o in self.owners]:
                        self.owners.append(new_owner)
                        self.save_config()
                        await self.highrise.chat(f"👑 تم إضافة @{new_owner} كمالك جديد")
                    else:
                        await self.highrise.send_whisper(user.id, "❌ هذا المستخدم مالك بالفعل")
                else:
                    await self.highrise.send_whisper(user.id, "❌ مثال: اضافة_مالك أحمد")
                return
            
            elif command in ["removeowner", "ازالة_مالك"]:
                if len(parts) >= 2:
                    old_owner = parts[1].lower()
                    if old_owner.startswith("@"):
                        old_owner = old_owner[1:]
                    original_owner = next((o for o in self.owners if o.lower() == old_owner), None)
                    if original_owner:
                        if len(self.owners) > 1:
                            self.owners.remove(original_owner)
                            self.save_config()
                            await self.highrise.chat(f"👑 تم إزالة @{old_owner} من قائمة الملاك")
                        else:
                            await self.highrise.send_whisper(user.id, "❌ لا يمكنك إزالة المالك الوحيد المتبقي!")
                    else:
                        await self.highrise.send_whisper(user.id, "❌ هذا المستخدم ليس مالكاً")
                else:
                    await self.highrise.send_whisper(user.id, "❌ مثال: ازالة_مالك أحمد")
                return
            
            elif command in ["owners", "الملاك"]:
                await self.highrise.chat(f"👑 الملاك الحاليين: {', '.join(self.owners)}")
                return
            
            elif command in ["reset", "ريست", "إعادة_تشغيل"]:
                self.muted_users.clear()
                self.frozen_users.clear()
                self.warned_users.clear()
                self.user_messages.clear()
                for user_id in list(self.dancing_users.keys()):
                    self.dancing_users[user_id].cancel()
                self.dancing_users.clear()
                await self.highrise.chat("🔄 تم إعادة تشغيل البوت ومسح جميع البيانات")
                return

    async def show_help(self, user: User):
        """عرض قائمة مساعدة روم المنتجع"""
        is_admin = await self.is_admin(user)
        is_owner = self.is_owner(user)
        
        help_msg = """🌿 روم المنتجع - قائمة الأوامر ✨
━━━━━━━━━━━━━━
📌 أوامر عامة:
help - المساعدة
users - المتواجدين
floors - استعراض الطوابق
رقصات - كيفية الرقص
0 - إيقاف الرقص

🏢 التنقل السريع:
ارضي / فوق / فوق2 / vip
        """
        await self.highrise.send_whisper(user.id, help_msg)
        await asyncio.sleep(0.5)

        interact_msg = """🌿 تفاعلات المنتجع (الأمر اسم_الشخص):
قلب، كف، حضن، بوس، لكم، ركل
ضحك، غزل، كفك، احترام، زواج
طيران، تليبورت، قيتار، انمي
        """
        await self.highrise.send_whisper(user.id, interact_msg)

        if is_admin:
            await asyncio.sleep(0.5)
            admin_msg = """🛡️ لوحة تحكم المشرفين:
طرد / كتم / حظر / تحذير <اسم>
جلب / br / روح <اسم> (انتقال)
تجميد / فك <اسم>
إعلان <رسالة> | مسح (تنظيف)
ر - قلوب للكل
            """
            await self.highrise.send_whisper(user.id, admin_msg)
            
        if is_owner:
            await asyncio.sleep(0.5)
            owner_msg = """👑 صلاحيات المالك:
اضف_مشرف / ازل_مشرف
اضافة_مالك / ريست / setbot
فلوس (عرض الجولد) | تميز <اسم>
            """
            await self.highrise.send_whisper(user.id, owner_msg)

    async def is_admin(self, user: User) -> bool:
        """التحقق من صلاحيات المشرف"""
        if user.username.lower() in [o.lower() for o in self.owners]:
            return True
        
        if user.username.lower() in [a.lower() for a in self.admins if a]:
            return True
        
        try:
            permissions = await self.highrise.get_room_privilege(user.id)
            if not isinstance(permissions, Exception):
                return permissions.moderator or permissions.designer
        except:
            pass
        
        return False
    
    def is_owner(self, user: User) -> bool:
        """التحقق من المالك"""
        return user.username.lower() in [o.lower() for o in self.owners]

    async def get_user_by_name(self, username: str) -> User | None:
        """الحصول على مستخدم من اسمه"""
        try:
            room_users = await self.highrise.get_room_users()
            username_clean = username.strip()
            if username_clean.startswith('@'):
                username_clean = username_clean[1:]
            username_lower = username_clean.lower()
            
            for user, _ in getattr(room_users, 'content', []):
                if user.username.lower() == username_lower:
                    return user
            
            for user, _ in getattr(room_users, 'content', []):
                if username_lower in user.username.lower():
                    return user
                    
        except Exception as e:
            print(f"Error searching for user: {e}")
        
        return None

    async def kick_user(self, username: str, admin_user: User):
        """طرد مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            if user.username.lower() in [o.lower() for o in self.owners]:
                await self.highrise.chat(f"👑 لا يمكن طرد المالك!")
                return
            
            # منع المشرفين من طرد بعضهم البعض
            is_target_admin = await self.is_admin(user)
            is_admin_user = await self.is_admin(admin_user)
            if is_target_admin and not self.is_owner(admin_user):
                await self.highrise.chat(f"🛡️ لا يمكن طرد مشرف آخر! فقط الملاك يمكنهم فعل ذلك.")
                return
            
            try:
                await self.highrise.moderate_room(user.id, "kick")
                await self.highrise.chat(f"👢 تم طرد {user.username}")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")

    async def ban_user(self, username: str, duration: int):
        """حظر مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            if user.username.lower() in [o.lower() for o in self.owners]:
                await self.highrise.chat(f"👑 لا يمكن حظر المالك!")
                return
            try:
                await self.highrise.moderate_room(user.id, "ban", duration)
                await self.highrise.chat(f"🔨 تم حظر {username} لمدة {duration} ثانية")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")

    async def unban_user(self, username: str):
        """فك حظر مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            # ✅ لا يوجد إجراء "unban" في Highrise API
            # الحظر ينتهي تلقائياً بعد انتهاء المدة المحددة
            await self.highrise.chat(f"ℹ️ لا يمكن فك الحظر يدوياً - سينتهي تلقائياً. ({username})")
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")

    async def mute_user(self, username: str, duration: int, admin_user: User = None):
        """كتم مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            if user.username.lower() in [o.lower() for o in self.owners]:
                await self.highrise.chat(f"👑 لا يمكن كتم المالك!")
                return
            
            # حماية المشرفين
            is_target_admin = await self.is_admin(user)
            if is_target_admin:
                await self.highrise.chat(f"🛡️ لا يمكن كتم المشرفين!")
                return
            
            try:
                try:
                    await self.highrise.moderate_room(user.id, "mute", duration)
                    await self.highrise.chat(f"🔇 تم كتم {user.username} لمدة {duration} ثانية")
                except:
                    await self.highrise.chat(f"🔇 تم كتم {user.username} محلياً لمدة {duration} ثانية")
                
                # تخزين معرف المستخدم في قائمة المكتومين
                self.muted_users[user.id] = True
                await self.highrise.send_whisper(user.id, f"🔇 تم كتمك لمدة {duration} ثانية")
                
                # تشغيل مؤقت الكتم في الخلفية (بدون await) حتى يمكن فك الكتم يدوياً
                async def auto_unmute():
                    await asyncio.sleep(duration)
                    if user.id in self.muted_users:
                        del self.muted_users[user.id]
                        try:
                            await self.highrise.chat(f"🔊 انتهى كتم {user.username} تلقائياً")
                        except:
                            pass
                
                asyncio.create_task(auto_unmute())
                
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")

    async def unmute_user(self, username: str):
        """فك كتم مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            if user.username.lower() in [o.lower() for o in self.owners]:
                await self.highrise.chat(f"👑 لا يمكن حظر المالك!")
                return
            
            # حماية المشرفين
            is_target_admin = await self.is_admin(user)
            if is_target_admin:
                await self.highrise.chat(f"🛡️ لا يمكن حظر المشرفين!")
                return
            try:
                # حذف المستخدم من قائمة المكتومين
                if user.id in self.muted_users:
                    del self.muted_users[user.id]
                    await self.highrise.chat(f"🔊 تم فك كتم {user.username}")
                else:
                    await self.highrise.chat(f"ℹ️ {user.username} غير مكتوم")
                    
            except Exception as e:
                print(f"General error in unmute: {e}")
                try:
                    await self.highrise.chat(f"✅ تم محاولة فك كتم {username}")
                except:
                    pass
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")

    async def warn_user(self, user: User, reason: str):
        """تحذير مستخدم"""
        if user.id not in self.warned_users:
            self.warned_users[user.id] = 0
        
        self.warned_users[user.id] += 1
        warns = self.warned_users[user.id]
        
        await self.highrise.send_whisper(user.id, f"⚠️ تحذير ({warns}/3): {reason}")
        await self.highrise.chat(f"⚠️ تم تحذير {user.username} - السبب: {reason}")
        
        if warns >= 3:
            await self.highrise.chat(f"🔨 تم حظر {user.username} بسبب تجاوز التحذيرات")
            await self.highrise.moderate_room(user.id, "kick")
            del self.warned_users[user.id]

    async def list_users(self):
        """عرض قائمة المستخدمين"""
        try:
            room_users = await self.highrise.get_room_users()
            
            if getattr(room_users, 'content', []):
                user_list = []
                for i, (user, _) in enumerate(getattr(room_users, 'content', []), 1):
                    user_list.append(f"{i}. @{user.username}")
                
                users_str = "\n".join(user_list)
                await self.highrise.chat(f"👥 المستخدمين ({len(user_list)}):\n{users_str}")
            else:
                await self.highrise.chat("لا يوجد مستخدمين في الغرفة")
        except Exception as e:
            await self.highrise.chat(f"❌ خطأ: {e}")

    async def check_spam(self, user: User) -> bool:
        """فحص السبام"""
        import time
        
        if user.id not in self.user_messages:
            self.user_messages[user.id] = []
        
        current_time = time.time()
        self.user_messages[user.id].append(current_time)
        
        self.user_messages[user.id] = [
            t for t in self.user_messages[user.id] 
            if current_time - t < 10
        ]
        
        return len(self.user_messages[user.id]) > 5
    
    async def freeze_user(self, username: str):
        """تجميد مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            if user.username.lower() in [o.lower() for o in self.owners]:
                await self.highrise.chat(f"👑 لا يمكن تجميد المالك!")
                return
            
            try:
                room_users = await self.highrise.get_room_users()
                for u, pos in getattr(room_users, 'content', []):
                    if u.id == user.id:
                        self.frozen_users[user.id] = pos
                        await self.highrise.chat(f"🧊 تم تجميد {user.username}")
                        await self.highrise.send_whisper(user.id, "⚠️ تم تجميدك!")
                        return
                await self.highrise.chat(f"❌ لم يتم العثور على موقع {user.username}")
            except Exception as e:
                await self.highrise.chat(f"❌ خطأ: {e}")
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")
    
    async def unfreeze_user(self, username: str):
        """فك تجميد مستخدم"""
        user = await self.get_user_by_name(username)
        if user:
            if user.id in self.frozen_users:
                del self.frozen_users[user.id]
                await self.highrise.chat(f"✅ تم فك تجميد {username}")
                await self.highrise.send_whisper(user.id, "✅ تم فك تجميدك!")
            else:
                await self.highrise.chat(f"❌ {username} غير مجمد")
        else:
            await self.highrise.chat(f"❌ لم يتم العثور على: {username}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        """عند استلام إكرامية"""
        try:
            # تسجيل المستخدم في سجل التفاعلات (للـ invite)
            self.interaction_history.add((sender.id, sender.username))
            
            if isinstance(tip, Item):
                if tip.amount > 1:
                    item_str = f"{tip.amount}x {tip.id}"
                else:
                    item_str = tip.id
                await self.highrise.chat(f"🎁 شكراً {sender.username} على الهدية الرائعة ({item_str})! 🙏 😍")
                
            elif isinstance(tip, CurrencyItem):
                await self.highrise.chat(f"💰 شكراً {sender.username} على {tip.amount} {tip.type}! أنت كريم جداً 🙏")
                
        except Exception as e:
            print(f"Error processing tip: {e}")

    async def on_whisper(self, user: User, message: str) -> None:
        """عند استلام رسالة خاصة"""
        try:
            self.interaction_history.add((user.id, user.username))
            print(f"Whisper from {user.username}: {message}")
            await self.handle_command(user, message)
        except Exception as e:
            print(f"Error in on_whisper: {e}")

    async def tip_user(self, sender: User, parts: list):
        """💰 نظام توزيع الجولد"""
        try:
            if len(parts) < 3:
                await self.safe_whisper(sender.id, "❌ مثال:\ntip اسم 100\ntip 5 50\ntip all 10")
                return

            if parts[1].lower() == "all":
                amount = int(parts[2])
                room_users = await self.highrise.get_room_users()
                count = 0
                await self.safe_chat(f"💵 جاري توزيع {amount} جولد على الجميع...")
                for u, _ in getattr(room_users, 'content', []):
                    if u.id != self.highrise.my_id:
                        try:
                            await self.highrise.tip_user_in_room(u.id, amount)
                            count += 1
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            print(f"Tip error for {u.username}: {e}")
                await self.safe_chat(f"✅ تم توزيع {amount} جولد على {count} شخص!")
                return

            try:
                count_target = int(parts[1])
                amount = int(parts[2])
                room_users = await self.highrise.get_room_users()
                users_list = [u for u, _ in getattr(room_users, 'content', []) if u.id != self.highrise.my_id]
                import random
                selected = random.sample(users_list, min(count_target, len(users_list)))
                await self.safe_chat(f"💵 جاري إعطاء {amount} جولد لـ {len(selected)} أشخاص عشوائيين...")
                for u in selected:
                    try:
                        await self.highrise.tip_user_in_room(u.id, amount)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        print(f"Tip error: {e}")
                names = "، ".join([u.username for u in selected[:5]])
                await self.safe_chat(f"✅ تم إعطاء {amount} جولد لـ: {names}{'...' if len(selected) > 5 else ''}")
                return
            except ValueError:
                pass

            target_name = parts[1]
            amount = int(parts[2])
            target_user = await self.get_user_by_name(target_name)
            if target_user:
                await self.highrise.tip_user_in_room(target_user.id, amount)
                await self.safe_chat(f"💵 تم إعطاء {amount} جولد لـ @{target_user.username}!")
            else:
                await self.safe_whisper(sender.id, f"❌ لم يتم العثور على: {target_name}")

        except ValueError:
            await self.safe_whisper(sender.id, "❌ الرقم غير صحيح")
        except Exception as e:
            await self.safe_whisper(sender.id, f"❌ خطأ: {e}")

    async def send_invites(self, sender: User, custom_message: str = ""):
        """📨 إرسال دعوات للمتفاعلين"""
        try:
            if not self.interaction_history:
                await self.safe_whisper(sender.id, "❌ لا يوجد أشخاص في سجل التفاعلات بعد")
                return
            invite_msg = custom_message if custom_message else "🌟 مرحباً! البوت يدعوك للانضمام إلى الروم!"
            await self.safe_whisper(sender.id, f"📨 جاري إرسال دعوات لـ {len(self.interaction_history)} شخص...")
            sent = 0
            for user_id, username in list(self.interaction_history):
                try:
                    await self.highrise.send_whisper(user_id, invite_msg)
                    sent += 1
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Invite error for {username}: {e}")
            await self.safe_whisper(sender.id, f"✅ تم إرسال الدعوة لـ {sent} شخص!")
        except Exception as e:
            await self.safe_whisper(sender.id, f"❌ خطأ: {e}")

    async def equip_bot_from_user(self, sender: User, target_username: str):
        """👗 نسخ ملابس مستخدم آخر"""
        try:
            target_user = await self.get_user_by_name(target_username)
            if not target_user:
                await self.safe_whisper(sender.id, f"❌ لم يتم العثور على: {target_username}")
                return
            await self.safe_whisper(sender.id, f"👗 جاري نسخ ملابس {target_user.username}...")
            user_outfit = await self.highrise.get_user_outfit(target_user.id)
            if user_outfit and hasattr(user_outfit, 'outfit'):
                await self.highrise.set_outfit(user_outfit.outfit)
                await self.safe_chat(f"👗 البوت يرتدي الآن ملابس {target_user.username}!")
            else:
                await self.safe_whisper(sender.id, "❌ لم أتمكن من جلب ملابس هذا المستخدم")
        except Exception as e:
            await self.safe_whisper(sender.id, f"❌ خطأ: {e}")

    async def switch_positions(self, requester: User, target_username: str):
        """🔄 تبديل موقع المشرف مع مستخدم"""
        try:
            target_user = await self.get_user_by_name(target_username)
            if not target_user:
                await self.safe_whisper(requester.id, f"❌ لم يتم العثور على: {target_username}")
                return
            # حماية الملاك والمشرفين
            is_target_owner = self.is_owner(target_user)
            is_target_admin = await self.is_admin(target_user)
            is_requester_owner = self.is_owner(requester)
            
            if (is_target_owner or is_target_admin) and not is_requester_owner:
                await self.safe_whisper(requester.id, f"🛡️ لا يمكنك تبديل الموقع مع الملاك أو المشرفين!")
                return

            room_users = await self.highrise.get_room_users()
            req_pos = next((pos for u, pos in getattr(room_users, 'content', []) if u.id == requester.id), None)
            target_pos = next((pos for u, pos in getattr(room_users, 'content', []) if u.id == target_user.id), None)
            if req_pos and target_pos and isinstance(req_pos, Position) and isinstance(target_pos, Position):
                await asyncio.gather(
                    self.highrise.teleport(requester.id, target_pos),
                    self.highrise.teleport(target_user.id, req_pos)
                )
                await self.safe_chat(f"🔄 تم تبديل موقع {requester.username} مع {target_user.username}!")
            else:
                await self.safe_whisper(requester.id, "❌ لم أتمكن من جلب المواقع")
        except Exception as e:
            await self.safe_whisper(requester.id, f"❌ خطأ: {e}")

    async def move_users(self, requester: User, user1_name: str, user2_name: str):
        """🔄 تبديل مواقع مستخدمين"""
        try:
            user1 = await self.get_user_by_name(user1_name)
            user2 = await self.get_user_by_name(user2_name)
            if not user1 or not user2:
                await self.safe_whisper(requester.id, "❌ لم يتم العثور على أحد المستخدمين")
                return
            # حماية الملاك والمشرفين
            is_u1_protected = self.is_owner(user1) or await self.is_admin(user1)
            is_u2_protected = self.is_owner(user2) or await self.is_admin(user2)
            is_requester_owner = self.is_owner(requester)
            
            if (is_u1_protected or is_u2_protected) and not is_requester_owner:
                await self.safe_whisper(requester.id, "🛡️ لا يمكنك نقل الملاك أو المشرفين!")
                return

            room_users = await self.highrise.get_room_users()
            pos1 = next((pos for u, pos in getattr(room_users, 'content', []) if u.id == user1.id), None)
            pos2 = next((pos for u, pos in getattr(room_users, 'content', []) if u.id == user2.id), None)
            if pos1 and pos2 and isinstance(pos1, Position) and isinstance(pos2, Position):
                await asyncio.gather(
                    self.highrise.teleport(user1.id, pos2),
                    self.highrise.teleport(user2.id, pos1)
                )
                await self.safe_chat(f"🔄 تم تبديل موقع {user1.username} مع {user2.username}!")
            else:
                await self.safe_whisper(requester.id, "❌ لم أتمكن من جلب المواقع")
        except Exception as e:
            await self.safe_whisper(requester.id, f"❌ خطأ: {e}")



if __name__ == "__main__":
    ROOM_ID = "695f30ddb10ff02e8ba0df4b"
    TOKEN = "007243ed44a910c0913006a6f206babde6d4dc1c2a68915d916a66b7f112f9fb"
    
    async def run_forever():
        while True:
            try:
                definitions = [BotDefinition(MyBot(), ROOM_ID, TOKEN)]
                await main(definitions)
            except Exception as e:
                print(f"Bot error: {e}. Restarting in 5s...")
                await asyncio.sleep(5)

    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        pass
