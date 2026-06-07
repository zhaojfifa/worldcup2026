/**
 * Burmese / Myanmar (mm) copy — MVP language mode (starting this sprint).
 *
 * Partial: covers the highest-frequency customer-visible surfaces. Any key not
 * present here falls back to English (NOT Chinese) via the dictionary chain
 * (mm → en). Full Burmese localization is deferred; LLM translation deferred.
 */
import type { Copy } from '../i18n/dict';

export const MM: Partial<Copy> = {
  // Header / brand
  brandRole: 'ကမ္ဘာ့ဖလား AI ဘောလုံးသတင်းအချက်အလက် အသိုင်းအဝိုင်း',
  headerSub: 'နှုန်းကိုသာမကြည့်ဘဲ AI ဘာကြောင့် ဤသို့ဆုံးဖြတ်သည်ကို နားလည်ပါ။',

  // Bottom nav
  navHome: 'ပင်မ',
  navDetail: 'AI ခန့်မှန်း',
  navToken: 'MTC',
  navCommunity: 'အသိုင်းအဝိုင်း',

  // Global
  aiTicker: 'AI သတင်း',
  loadingText: 'AI သတင်း ဖွင့်နေသည်…',
  syncLabel: 'ထပ်တူ',

  // Hero
  heroTitlePre: 'ဘောလုံး ',
  heroTitleAccent: 'AI သတင်း',
  heroSub: 'AI အမြင် · နှုန်းပြောင်းလဲမှု · အန္တရာယ်သတိပေးချက် · ပွဲချိန်ပြင်ဆင်မှု',

  // Capability chips
  capModel: 'AI ပွဲမတိုင်မီ မော်ဒယ်',
  capLive: 'ပွဲချိန် ၃၀ မိနစ် ပြင်ဆင်မှု',
  capRisk: 'အန္တရာယ် အဆင့်သတ်မှတ်',
  capUnlock: 'MTC ဖွင့်ရန်',

  // Balance / check-in
  balanceLabel: 'ကျွန်ုပ်၏ MTC ပွိုင့်: ',
  checkin: 'ဝင်စစ် +10',
  checkedIn: 'စစ်ဆေးပြီး',
  checkinToastDone: 'ယနေ့ စစ်ဆေးပြီးပါပြီ',
  checkinToastOk: 'ဝင်ရောက်စစ်ဆေးအောင်မြင် +10 MTC',

  // Home core + CTA
  signalTitle: 'ယနေ့ အကောင်းဆုံး AI signal',
  tendency: 'AI ခန့်မှန်းချက်',
  topRisk: 'အဓိက အန္တရာယ်',
  ctaView: 'AI အမြင် ကြည့်ရန်',
  ctaUnlock: 'အပြည့်အစုံ ခွဲခြမ်းစိတ်ဖြာချက် ဖွင့်ရန်',
  winLabel: 'နိုင်',

  // Section titles + states
  listTitle: 'ယနေ့ ပွဲစဉ်များ',
  upsetTitle: 'ယနေ့ အံ့အားသင့်နိုင်ခြေ TOP3',
  recordTitle: 'AI သတင်း မှတ်တမ်း',
  heatTitle: 'အသိုင်းအဝိုင်း ရွေးချယ်မှု',
  loopTitle: 'ပရိသတ် တာဝန်စင်တာ',
  recordPending: 'တကယ့်ရလဒ်များ ဖြည့်ပြီးမှ ဖွင့်မည်',
  recordBuilding: 'ဒေတာစွမ်းရည် တည်ဆောက်နေသည်',
  heatComingSoon: 'အသိုင်းအဝိုင်း ပူပြင်းမှု မကြာမီ',
  loopFanPoints: 'ပရိသတ်ပွိုင့်',
  loopDailyCheckin: 'နေ့စဉ်စစ်ဆေး',
  loopStreak: 'ဆက်တိုက်နိုင်ပွဲ စိန်ခေါ်မှု',
  loopFreeJoin: 'အခမဲ့ ပါဝင်',
  loopRanking: 'အဆင့်သတ်မှတ်ဇယား',
  loopComingSoon: 'မကြာမီ',

  // Detail
  detailBack: 'ပွဲ ခန့်မှန်းချက် အသေးစိတ်',
  aiVerdict: 'AI ကောက်ချက်',
  confidence: 'ယုံကြည်မှု',
  riskGrade: 'အန္တရာယ်အဆင့်',
  recommendedScore: 'အကြံပြု ရမှတ်',
  unlockToView: 'ဖွင့်ကြည့်ရန်',
  winProbTitle: 'AI လက်ရှိ နိုင်ခြေ',
  whyTitle: 'AI ဘာကြောင့် ဤသို့ဆုံးဖြတ်သလဲ',
  riskTitle: 'အန္တရာယ် အချက်များ',
  premiumTitle: 'AI နည်းဗျူဟာ ဖွင့်ချက်',
  premiumLocked: '🔒 မဖွင့်ရသေး',
  unlockCashLabel: 'AI နည်းဗျူဟာ ဖွင့်ရန်',
  unlockMtcLabel: '🪙 မော်ဒယ် ရှင်းလင်းချက် အပြည့်အစုံ ကြည့်ရန်',
  joinCommunityLabel: 'ပွဲချိန်သတင်း အသိုင်းအဝိုင်း ဝင်ရန်',

  // Token
  tokenBack: '🪙 ပရိသတ် တာဝန်စင်တာ',
  walletLabel: 'ကျွန်ုပ်၏ MTC ပွိုင့်လက်ကျန်',
  myStreak: 'ကျွန်ုပ်၏ ဆက်တိုက်နိုင်ပွဲ',
  dailyMissions: 'နေ့စဉ် တာဝန်များ',
  predictionChallenge: 'ခန့်မှန်း စိန်ခေါ်မှု',
  shopTitle: 'ပွိုင့် လဲလှယ်ရန်',
  rankingsTitle: 'ဆက်တိုက်နိုင်ပွဲ အဆင့်ဇယား',
  tokenInsufficient: 'MTC ပွိုင့် မလုံလောက်ပါ',

  // Community
  communityBack: '👥 ပွဲချိန်သတင်း VIP',
  vipKicker: 'ပွဲချိန်သတင်း VIP',
  communityTitle: 'အသိုင်းအဝိုင်း ကွန်ရက်',
  statusComingSoon: 'မကြာမီ',
  statusActive: 'ကြည့်ရန်',
  statusDisabled: 'မဖွင့်သေး',
  benefitsTitle: 'အသင်းဝင် အခွင့်အရေး',
  subscribeNowLabel: 'ယခု စာရင်းသွင်းရန်',
  alreadySubscribed: 'စာရင်းသွင်းပြီး',

  // Compliance
  mtcStatement: 'MTC သည် ပလက်ဖောင်းပွိုင့်သာဖြစ်ပြီး ငွေထုတ်မရ၊ လွှဲမရ၊ ရောင်းဝယ်မရ၊ ဘဏ္ဍာရေးပိုင်ဆိုင်မှု မဟုတ်ပါ။',
  disclaimer: 'အတိတ်စွမ်းဆောင်ရည်သည် အနာဂတ်ရလဒ်ကို အာမမခံပါ။ ဒေတာခွဲခြမ်းစိတ်ဖြာမှုနှင့် ဘောလုံးဖျော်ဖြေရေးအတွက်သာ။',
  complianceFooter: 'AI ဒေတာခွဲခြမ်းစိတ်ဖြာမှုသာ · လောင်းကစားဝန်ဆောင်မှု မဟုတ် · ငွေသားလောင်းကစား မရှိ · MTC ငွေထုတ်မရ',
};
