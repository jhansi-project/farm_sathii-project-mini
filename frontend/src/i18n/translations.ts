/**
 * Application-wide Translations Dictionary for FarmSathi.
 * Pure farmer-friendly translations in English, Telugu (తెలుగు), Hindi (हिन्दी),
 * Tamil (தமிழ்), Kannada (ಕನ್ನಡ), and Marathi (मराठी).
 */

export type LanguageCode = 'en' | 'te' | 'hi' | 'ta' | 'kn' | 'mr';

export interface TranslationDictionary {
  nav: {
    brand: string;
    home: string;
    ask: string;
    myCrops: string;
    diagnosis: string;
    cropRecommendation: string;
    history: string;
    profile: string;
    login: string;
    logout: string;
    selectLocation: string;
    detectLocation: string;
  };
  welcome: {
    title: string;
    tagline: string;
    description: string;
    selectLanguagePrompt: string;
    continueButton: string;
    cropRec: string;
    cropRecDesc: string;
    disease: string;
    diseaseDesc: string;
    weather: string;
    weatherDesc: string;
  };
  permissions: {
    title: string;
    subtitle: string;
    optionalBadge: string;
    locationTitle: string;
    locationDesc: string;
    locationDetecting: string;
    locationEnabled: string;
    locationAllow: string;
    locationManualOption: string;
    locationUnavailable: string;
    locationContext: string;
    cameraTitle: string;
    cameraDesc: string;
    cameraReady: string;
    cameraContext: string;
    cameraEnabled: string;
    cameraAllow: string;
    cameraFallback: string;
    micTitle: string;
    micDesc: string;
    micReady: string;
    micContext: string;
    micEnabled: string;
    micAllow: string;
    micFallback: string;
    optionalNotice: string;
    skipForNow: string;
    continue: string;
  };
  dashboard: {
    greeting: string;
    heroTitle: string;
    heroSubtitle: string;
    askPlaceholder: string;
    askButton: string;
    quickActions: string;
    actionCropRec: string;
    actionCropRecDesc: string;
    actionDiagnosis: string;
    actionDiagnosisDesc: string;
    actionAsk: string;
    actionAskDesc: string;
    actionMyCrops: string;
    actionMyCropsDesc: string;
    recentActivity: string;
    noActivity: string;
    noActivityDesc: string;
    viewAll: string;
  };
  weather: {
    cardTitle: string;
    temperature: string;
    humidity: string;
    rainfall: string;
    wind: string;
    forecast: string;
    loading: string;
    unavailable: string;
    selectLocationPrompt: string;
  };
  cropRec: {
    title: string;
    subtitle: string;
    soilNutrients: string;
    nitrogen: string;
    nitrogenPlaceholder: string;
    phosphorus: string;
    phosphorusPlaceholder: string;
    potassium: string;
    potassiumPlaceholder: string;
    climateConditions: string;
    temperature: string;
    temperaturePlaceholder: string;
    humidity: string;
    humidityPlaceholder: string;
    ph: string;
    phPlaceholder: string;
    rainfall: string;
    rainfallPlaceholder: string;
    fillFromWeather: string;
    calculateButton: string;
    calculating: string;
    resultTitle: string;
    whyThisCrop: string;
    whyDesc: string;
    inputSummary: string;
    checkAnother: string;
  };
  disease: {
    title: string;
    subtitle: string;
    takePhoto: string;
    uploadPhoto: string;
    changePhoto: string;
    diagnoseButton: string;
    diagnosing: string;
    resultTitle: string;
    cropDetected: string;
    conditionDetected: string;
    confidenceLabel: string;
    healthyFoliage: string;
    diseaseDetected: string;
    managementGuidance: string;
    culturalPractices: string;
    sanitation: string;
    prevention: string;
    disclaimer: string;
    scanAnother: string;
    emptyUploadPrompt: string;
    unsuitableTitle: string;
    unsuitablePrompt: string;
    retakePhoto: string;
  };
  ask: {
    title: string;
    subtitle: string;
    inputPlaceholder: string;
    speak: string;
    listening: string;
    stop: string;
    send: string;
    commonQuestions: string;
    q1: string;
    q2: string;
    q3: string;
    q4: string;
    consulting: string;
    loginRequired: string;
    loginToAsk: string;
    submitQuestion: string;
    submitWithPhoto: string;
    retry: string;
    errorTitle: string;
  };
  myCrops: {
    title: string;
    subtitle: string;
    addCrop: string;
    cropName: string;
    cropNamePlaceholder: string;
    emptyTitle: string;
    emptySubtitle: string;
    findCropButton: string;
    activeCrops: string;
    plantedOn: string;
    recommendedConditions: string;
  };
  history: {
    title: string;
    subtitle: string;
    tabAll: string;
    tabCrops: string;
    tabDiagnosis: string;
    tabAdvisory: string;
    emptyTitle: string;
    emptySubtitle: string;
  };
  common: {
    loading: string;
    save: string;
    cancel: string;
    close: string;
    error: string;
    tryAgain: string;
    guestMode: string;
    saved: string;
    searchLocation: string;
    useCurrentLocation: string;
    enterCityName: string;
    search: string;
    locationNotFound: string;
    voice_input: string;
    speak_placeholder: string;
    camera_upload: string;
    disease_detection: string;
    crop_recommendation: string;
    advisory: string;
    recent_activity: string;
    no_activity: string;
    no_activity_desc: string;
    ask_new_question: string;
    ask_question: string;
    queries: string;
    type_placeholder: string;
    foliage_context: string;
    crop_health: string;
    all: string;
    back: string;
    listening: string;
    reverse_geocoding_failed: string;
  };
}

export const translations: Record<LanguageCode, TranslationDictionary> = {
  en: {
    nav: {
      brand: 'FarmSathi',
      home: 'Home',
      ask: 'Ask',
      myCrops: 'My Crops',
      diagnosis: 'Diagnosis',
      cropRecommendation: 'Crop Recommendation',
      history: 'History',
      profile: 'Profile',
      login: 'Login',
      logout: 'Logout',
      selectLocation: 'Select Location',
      detectLocation: 'Detect GPS Location',
    },
    welcome: {
      title: 'Welcome to FarmSathi',
      tagline: 'Your Digital Agricultural Companion',
      description:
        'FarmSathi empowers Indian farmers with precision crop recommendations, plant disease detection, verified local weather forecasts, and expert agricultural guidance.',
      selectLanguagePrompt: 'Choose Your Preferred Language',
      continueButton: 'Continue to FarmSathi',
      cropRec: 'Smart Crop Recommendation',
      cropRecDesc: 'Identify the highest-yielding crop for your soil nutrients and climate.',
      disease: 'Instant Leaf Diagnosis',
      diseaseDesc: 'Scan crop foliage to detect diseases and receive organic management tips.',
      weather: 'Verified Agro-Weather',
      weatherDesc: 'Real-time rainfall outlook, temperature, and local farming advisories.',
    },
    permissions: {
      title: 'Set Up FarmSathi',
      subtitle: 'Tell us what permissions you would like FarmSathi to use.',
      optionalBadge: 'Optional',
      locationTitle: 'Location',
      locationDesc: 'Use location for local weather, rainfall forecasts, and regional farming advice.',
      locationDetecting: 'Detecting location...',
      locationEnabled: 'Location Detected',
      locationAllow: 'Use Current Location',
      locationManualOption: 'Select Location Manually',
      locationUnavailable: 'Location unavailable. You can select your district manually anytime.',
      locationContext: 'Local weather & context',
      cameraTitle: 'Camera',
      cameraDesc: 'Take photos of affected crop leaves for disease diagnosis and care advice.',
      cameraReady: 'Ready for Crop Photos',
      cameraContext: 'Crop disease photos',
      cameraEnabled: 'Camera Ready',
      cameraAllow: 'Allow Camera',
      cameraFallback: 'Photo upload available from gallery',
      micTitle: 'Microphone',
      micDesc: 'Speak your farming and weather questions naturally in your preferred language.',
      micReady: 'Ready for Voice Questions',
      micContext: 'Voice questions in your language',
      micEnabled: 'Microphone Ready',
      micAllow: 'Allow Microphone',
      micFallback: 'Text typing always available',
      optionalNotice:
        'Permissions are optional. If denied, you can always select locations manually, upload photos from your device, and type your questions.',
      skipForNow: 'Skip for Now',
      continue: 'Continue to FarmSathi',
    },
    dashboard: {
      greeting: 'Welcome, Farmer',
      heroTitle: 'Your Smart Farming Companion',
      heroSubtitle:
        "Check today's weather, scan crop health, calculate the best crop, or ask any agricultural question.",
      askPlaceholder: 'Ask anything about your crop, rain, fertilizer, or soil...',
      askButton: 'Ask',
      quickActions: 'Core Farming Services',
      actionCropRec: 'Find Best Crop',
      actionCropRecDesc: 'Soil-based AI recommendation',
      actionDiagnosis: 'Diagnose Crop Disease',
      actionDiagnosisDesc: 'Scan leaf photos for health & remedies',
      actionAsk: 'Ask Agricultural Advisor',
      actionAskDesc: 'Instant guidance on farming questions',
      actionMyCrops: 'My Crops',
      actionMyCropsDesc: 'Track your field crops & care steps',
      recentActivity: 'Recent Farm Activity',
      noActivity: 'No recent activity yet.',
      noActivityDesc:
        'Ask a question, diagnose a crop leaf, or get a crop recommendation to see your farm history here.',
      viewAll: 'View All History',
    },
    weather: {
      cardTitle: "Today's Farm Weather",
      temperature: 'Temperature',
      humidity: 'Relative Humidity',
      rainfall: 'Rainfall / Precipitation',
      wind: 'Wind Speed',
      forecast: '7-Day Weather Outlook',
      loading: 'Fetching real-time weather...',
      unavailable: 'Weather information unavailable.',
      selectLocationPrompt: 'Please select or allow your location to view live weather.',
    },
    cropRec: {
      title: 'Find the Best Crop for Your Field',
      subtitle:
        'Enter your soil nutrient levels and climate conditions to calculate the scientific best-match crop.',
      soilNutrients: 'Soil Nutrients (N - P - K)',
      nitrogen: 'Nitrogen (N) - kg/ha',
      nitrogenPlaceholder: 'Enter nitrogen value (e.g., 20 - 140)',
      phosphorus: 'Phosphorus (P) - kg/ha',
      phosphorusPlaceholder: 'Enter phosphorus value (e.g., 10 - 100)',
      potassium: 'Potassium (K) - kg/ha',
      potassiumPlaceholder: 'Enter potassium value (e.g., 10 - 100)',
      climateConditions: 'Climate & Soil Conditions',
      temperature: 'Temperature (°C)',
      temperaturePlaceholder: 'Enter temperature (e.g., 15 - 40)',
      humidity: 'Relative Humidity (%)',
      humidityPlaceholder: 'Enter humidity (e.g., 30 - 90)',
      ph: 'Soil pH (0 - 14)',
      phPlaceholder: 'Enter soil pH (e.g., 5.5 - 7.5)',
      rainfall: 'Annual Rainfall (mm)',
      rainfallPlaceholder: 'Enter rainfall (e.g., 100 - 300)',
      fillFromWeather: 'Fill Temperature & Humidity from Current Weather',
      calculateButton: 'Calculate Recommended Crop',
      calculating: 'Analyzing soil & climate conditions...',
      resultTitle: 'Recommended Crop',
      whyThisCrop: 'Why this crop?',
      whyDesc:
        'Based on the soil nutrients, soil pH, and climate conditions you entered, this crop provides optimal growth suitability and yield potential.',
      inputSummary: 'Input Summary',
      checkAnother: 'Evaluate Another Field',
    },
    disease: {
      title: 'Crop Leaf Disease Diagnosis',
      subtitle:
        'Upload or capture a photo of affected crop foliage for instant diagnosis and organic cultural management advice.',
      takePhoto: 'Take Photo with Camera',
      uploadPhoto: 'Upload from Gallery',
      changePhoto: 'Change Photo',
      diagnoseButton: 'Diagnose Crop Health',
      diagnosing: 'Analyzing foliage health...',
      resultTitle: 'Disease Detection Result',
      cropDetected: 'Crop',
      conditionDetected: 'Detected Condition',
      confidenceLabel: 'Confidence',
      healthyFoliage: 'Healthy Foliage Detected',
      diseaseDetected: 'Disease Symptoms Detected',
      managementGuidance: 'Agronomic & Cultural Care',
      culturalPractices: 'Cultural Practices',
      sanitation: 'Field Sanitation',
      prevention: 'Preventive Measures',
      disclaimer:
        'Consult your local agricultural extension service or Krishi Vigyan Kendra (KVK) for regional chemical spray advisories.',
      scanAnother: 'Scan Another Leaf',
      emptyUploadPrompt: 'Please select or capture a crop leaf photo first.',
      unsuitableTitle: 'Image not suitable for crop disease detection',
      unsuitablePrompt:
        'Please capture or upload a clear close-up photograph of an affected crop leaf.',
      retakePhoto: 'Retake Photo',
    },
    ask: {
      title: 'Ask FarmSathi',
      subtitle: 'Ask any question about your crops, weather, pest protection, or fertilizers.',
      inputPlaceholder: 'Type your farming question here...',
      speak: 'Speak',
      listening: 'Listening... speak clearly',
      stop: 'Stop',
      send: 'Send',
      commonQuestions: 'Common Farmer Inquiries',
      q1: 'Will it rain today on my farm?',
      q2: 'How to manage leaf blast in paddy?',
      q3: 'What is the recommended fertilizer schedule for wheat?',
      q4: 'When should I irrigate my crops?',
      consulting: 'Consulting FarmSathi Advisory Engine...',
      loginRequired: 'Sign in is required to ask questions and receive personalized agricultural advice.',
      loginToAsk: 'Sign In to Ask',
      submitQuestion: 'Ask FarmSathi',
      submitWithPhoto: 'Submit Question & Image',
      retry: 'Retry',
      errorTitle: 'Advisory Consultation Notice',
    },
    myCrops: {
      title: 'My Crops',
      subtitle: 'Track your active field crops, soil recommendations, and growth stages.',
      addCrop: 'Add Crop to Monitor',
      cropName: 'Crop Name',
      cropNamePlaceholder: 'Enter crop name (e.g., Rice, Cotton)',
      emptyTitle: 'No crops added yet.',
      emptySubtitle:
        'Get a personalized crop recommendation or record your active crops to monitor their growth and care here.',
      findCropButton: 'Find Recommended Crop',
      activeCrops: 'Active Crops',
      plantedOn: 'Planted on',
      recommendedConditions: 'Recommended Conditions',
    },
    history: {
      title: 'Farm History',
      subtitle: 'View your past crop recommendations, disease scans, and agricultural advisory sessions.',
      tabAll: 'All Activity',
      tabCrops: 'Crop Recommendations',
      tabDiagnosis: 'Disease Diagnoses',
      tabAdvisory: 'Advisories',
      emptyTitle: 'No activity yet.',
      emptySubtitle: 'Your crop recommendations, disease scans, and advisory questions will be saved here.',
    },
    common: {
      loading: 'Loading...',
      save: 'Save',
      cancel: 'Cancel',
      close: 'Close',
      error: 'An error occurred',
      tryAgain: 'Try Again',
      guestMode: 'Guest Mode',
      saved: 'Saved to Farm History',
      searchLocation: 'Search City or Village',
      useCurrentLocation: 'Use GPS Location',
      enterCityName: 'Enter city or district name...',
      search: 'Search',
      locationNotFound: 'No matching location found. Please try another search.',
      voice_input: 'Voice Input',
      speak_placeholder: 'Speak Question',
      camera_upload: 'Add Image',
      disease_detection: 'Disease Detection',
      crop_recommendation: 'Crop Recommendation',
      advisory: 'Advisory',
      recent_activity: 'Recent Farm Activity',
      no_activity: 'No recent activity yet.',
      no_activity_desc: 'Your advisory questions, crop recommendations, and plant diagnoses will appear here.',
      ask_new_question: 'New Session',
      ask_question: 'Ask Question',
      queries: 'Queries',
      type_placeholder: 'Type your farming question here...',
      foliage_context: 'Foliage Context',
      crop_health: 'Crop Health',
      all: 'All Activity',
      back: 'Back',
      listening: 'Listening...',
      reverse_geocoding_failed: 'Could not determine city name from coordinates. Please select manually.',
    },
  },

  te: {
    nav: {
      brand: 'ఫార్మ్‌సాథి',
      home: 'హోమ్',
      ask: 'ప్రశ్నించండి',
      myCrops: 'నా పంటలు',
      diagnosis: 'వ్యాధి నిర్ధారణ',
      cropRecommendation: 'పంట సిఫార్సు',
      history: 'చరిత్ర',
      profile: 'ప్రొఫైల్',
      login: 'లాగిన్',
      logout: 'లాగౌట్',
      selectLocation: 'లొకేషన్ ఎంచుకోండి',
      detectLocation: 'GPS లొకేషన్ గుర్తించండి',
    },
    welcome: {
      title: 'ఫార్మ్‌సాథికి స్వాగతం',
      tagline: 'మీ డిజిటల్ వ్యవసాయ సహాయకుడు',
      description:
        'ఫార్మ్‌సాథి భారతీయ రైతులకు పంట సిఫార్సులు, ఆకు తెగుళ్ల గుర్తింపు, ఖచ్చితమైన వాతావరణ సమాచారం మరియు వ్యవసాయ నిపుణుల సలహాలను అందిస్తుంది.',
      selectLanguagePrompt: 'మీ భాషను ఎంచుకోండి',
      continueButton: 'యాప్‌లోకి కొనసాగండి',
      cropRec: 'తెలివైన పంట సిఫార్సు',
      cropRecDesc: 'మీ నేల N-P-K మరియు వాతావరణానికి అనువైన ఉత్తమ పంటను ఎంచుకోండి.',
      disease: 'తక్షణ ఆకు వ్యాధి నిర్ధారణ',
      diseaseDesc: 'ఆకు ఫోటో తీసి తెగుళ్లను గుర్తించి సహజ నివారణ మార్గాలు పొందండి.',
      weather: 'ఖచ్చితమైన వ్యవసాయ వాతావరణం',
      weatherDesc: 'లైవ్ వర్ష సూచన, ఉష్ణోగ్రత మరియు పంట రక్షణ సలహాలు.',
    },
    permissions: {
      title: 'ఫార్మ్‌సాథి అమరికలు',
      subtitle: 'ఫార్మ్‌సాథి సేవలు సమర్థవంతంగా పనిచేయడానికి అనుమతులను ఎంచుకోండి.',
      optionalBadge: 'ఐచ్ఛికం',
      locationTitle: 'లొకేషన్',
      locationDesc: 'స్థానిక వాతావరణం, వర్షపాతం మరియు ప్రాంతీయ వ్యవసాయ సలహాల కోసం.',
      locationDetecting: 'లొకేషన్ గుర్తిస్తున్నాం...',
      locationEnabled: 'లొకేషన్ గుర్తించబడింది',
      locationAllow: 'ప్రస్తుత లొకేషన్ ఉపయోగించండి',
      locationManualOption: 'లొకేషన్‌ను స్వయంగా ఎంచుకోండి',
      locationUnavailable: 'లొకేషన్ అందుబాటులో లేదు. మీరు ఎప్పుడైనా జిల్లాను ఎంచుకోవచ్చు.',
      locationContext: 'వాతావరణం & ప్రాంతీయ సమాచారం',
      cameraTitle: 'కెమెరా',
      cameraDesc: 'పంట ఆకులకు సోకిన తెగుళ్ల నిర్ధారణ కోసం ఫోటో తీయండి.',
      cameraReady: 'ఆకు ఫోటోలకు సిద్ధం',
      cameraContext: 'తెగుళ్ల నిర్ధారణ ఫోటోలు',
      cameraEnabled: 'కెమెరా సిద్ధంగా ఉంది',
      cameraAllow: 'కెమెరాను అనుమతించండి',
      cameraFallback: 'గ్యాలరీ నుండి ఫోటో ఎంచుకోవచ్చు',
      micTitle: 'మైక్రోఫోన్',
      micDesc: 'మీ వ్యవసాయ ప్రశ్నలను మీ భాషలోనే మాట్లాడి అడగండి.',
      micReady: 'వాయిస్ ప్రశ్నలకు సిద్ధం',
      micContext: 'మీ భాషలో వాయిస్ ప్రశ్నలు',
      micEnabled: 'మైక్రోఫోన్ సిద్ధంగా ఉంది',
      micAllow: 'మైక్రోఫోన్‌ను అనుమతించండి',
      micFallback: 'టైప్ చేయడం ద్వారా ప్రశ్నలు అడగవచ్చు',
      optionalNotice:
        'ఈ అనుమతులు ఐచ్ఛికం. అనుమతించకపోయినా మీరు మాన్యువల్‌గా లొకేషన్ ఎంచుకోవచ్చు మరియు ఫోటోలు అప్‌లోడ్ చేయవచ్చు.',
      skipForNow: 'ఇప్పటికి దాటవేయండి',
      continue: 'కొనసాగించండి',
    },
    dashboard: {
      greeting: 'స్వాగతం, రైతు మిత్రమా',
      heroTitle: 'మీ డిజిటల్ వ్యవసాయ సహాయకుడు',
      heroSubtitle:
        'నేటి వాతావరణం, పంట ఆరోగ్యం, సరైన పంట ఎంపిక లేదా వ్యవసాయ సందేహాలను అడగండి.',
      askPlaceholder: 'మీ పంట, వర్షం, ఎరువులు లేదా నేల గురించి ఏదైనా అడగండి...',
      askButton: 'అడగండి',
      quickActions: 'ముఖ్య వ్యవసాయ సేవలు',
      actionCropRec: 'ఉత్తమ పంట ఎంపిక',
      actionCropRecDesc: 'నేల ఆధారిత AI పంట సిఫార్సు',
      actionDiagnosis: 'పంట తెగులు నిర్ధారణ',
      actionDiagnosisDesc: 'ఆకు ఫోటోతో వ్యాధి గుర్తింపు & నివారణ',
      actionAsk: 'వ్యవసాయ నిపుణుడిని అడగండి',
      actionAskDesc: 'వ్యవసాయ సందేహాలకు తక్షణ సమాధానాలు',
      actionMyCrops: 'నా పంటలు',
      actionMyCropsDesc: 'మీ పంటల పెరుగుదల & సంరక్షణ నమోదు',
      recentActivity: 'ఇటీవలి వ్యవసాయ వివరాలు',
      noActivity: 'ఇటీవలి వివరాలు ఏవీ లేవు.',
      noActivityDesc:
        'సందేహాలు అడగడం, తెగులు నిర్ధారించడం లేదా పంట సిఫార్సు చేయడం ద్వారా మీ చరిత్ర ఇక్కడ కనిపిస్తుంది.',
      viewAll: 'మొత్తం చరిత్రను చూడండి',
    },
    weather: {
      cardTitle: 'నేటి పొలం వాతావరణం',
      temperature: 'ఉష్ణోగ్రత',
      humidity: 'గాలిలో తేమ',
      rainfall: 'వర్షపాతం సూచన',
      wind: 'గాలి వేగం',
      forecast: '7 రోజుల వాతావరణ సూచన',
      loading: 'లైవ్ వాతావరణం పొందుతున్నాం...',
      unavailable: 'వాతావరణ సమాచారం అందుబాటులో లేదు.',
      selectLocationPrompt: 'వాతావరణం చూడటానికి మీ లొకేషన్‌ను ఎంచుకోండి.',
    },
    cropRec: {
      title: 'మీ పొలానికి అనువైన ఉత్తమ పంట',
      subtitle:
        'మీ నేల సారం (N-P-K) మరియు వాతావరణ వివరాలను నమోదు చేసి సరైన పంటను ఎంచుకోండి.',
      soilNutrients: 'నేల పోషకాలు (N - P - K)',
      nitrogen: 'నత్రజని (N) - కేజీ/హెక్టారు',
      nitrogenPlaceholder: 'నత్రజని విలువ (ఉదా: 20 - 140)',
      phosphorus: 'భాస్వరం (P) - కేజీ/హెక్టారు',
      phosphorusPlaceholder: 'భాస్వరం విలువ (ఉదా: 10 - 100)',
      potassium: 'పొటాష్ (K) - కేజీ/హెక్టారు',
      potassiumPlaceholder: 'పొటాష్ విలువ (ఉదా: 10 - 100)',
      climateConditions: 'వాతావరణం & నేల పరిస్థితులు',
      temperature: 'ఉష్ణోగ్రత (°C)',
      temperaturePlaceholder: 'ఉష్ణోగ్రత నమోదు చేయండి (15 - 40)',
      humidity: 'తేమ శాతం (%)',
      humidityPlaceholder: 'తేమ నమోదు చేయండి (30 - 90)',
      ph: 'నేల pH (0 - 14)',
      phPlaceholder: 'pH విలువ (ఉదా: 5.5 - 7.5)',
      rainfall: 'వార్షిక వర్షపాతం (మి.మీ)',
      rainfallPlaceholder: 'వర్షపాతం (ఉదా: 100 - 300)',
      fillFromWeather: 'ప్రస్తుత వాతావరణం నుండి ఉష్ణోగ్రత, తేమను నింపండి',
      calculateButton: 'సిఫార్సు చేసిన పంటను లెక్కించండి',
      calculating: 'నేల & వాతావరణాన్ని విశ్లేషిస్తున్నాం...',
      resultTitle: 'సిఫార్సు చేయబడిన పంట',
      whyThisCrop: 'ఈ పంట ఎందుకు అనుకూలం?',
      whyDesc:
        'మీరు నమోదు చేసిన నేల పోషకాలు, pH మరియు వాతావరణ పరిస్థితుల ప్రకారం ఈ పంట అధిక దిగుబడిని ఇస్తుంది.',
      inputSummary: 'నమోదు చేసిన వివరాలు',
      checkAnother: 'మరొక పొలం కోసం తనిఖీ చేయండి',
    },
    disease: {
      title: 'పంట ఆకు వ్యాధి నిర్ధారణ',
      subtitle:
        'వ్యాధి సోకిన ఆకు ఫోటో తీసి తక్షణ నివారణ మరియు సేంద్రీయ చర్యలను తెలుసుకోండి.',
      takePhoto: 'కెమెరాతో ఫోటో తీయండి',
      uploadPhoto: 'గ్యాలరీ నుండి ఎంచుకోండి',
      changePhoto: 'ఫోటో మార్చండి',
      diagnoseButton: 'ఆరోగ్యాన్ని విశ్లేషించండి',
      diagnosing: 'ఆకును పరిశీలిస్తున్నాం...',
      resultTitle: 'వ్యాధి నిర్ధారణ ఫలితం',
      cropDetected: 'పంట',
      conditionDetected: 'గుర్తించిన వ్యాధి / పరిస్థితి',
      confidenceLabel: 'ఖచ్చితత్వం',
      healthyFoliage: 'ఆరోగ్యకరమైన పంట',
      diseaseDetected: 'వ్యాధి లక్షణాలు గుర్తించబడ్డాయి',
      managementGuidance: 'నివారణ & వ్యవసాయ చర్యలు',
      culturalPractices: 'సాగు పద్ధతులు',
      sanitation: 'పొలం పరిశుభ్రత',
      prevention: 'ముందస్తు జాగ్రత్తలు',
      disclaimer:
        'రసాయన మందుల వివరాల కోసం స్థానిక వ్యవసాయ అధికారి లేదా కృషి విజ్ఞాన కేంద్రాన్ని (KVK) సంప్రదించండి.',
      scanAnother: 'మరొక ఆకును తనిఖీ చేయండి',
      emptyUploadPrompt: 'దయచేసి ముందుగా ఆకు ఫోటోను ఎంచుకోండి.',
      unsuitableTitle: 'ఈ చిత్రం పంట తెగుళ్ల గుర్తింపునకు అనువైనది కాదు',
      unsuitablePrompt:
        'దయచేసి ప్రభావిత పంట ఆకు యొక్క స్పష్టమైన క్లోజప్ ఫోటోను తీయండి లేదా అప్‌లోడ్ చేయండి.',
      retakePhoto: 'మళ్లీ ఫోటో తీయండి',
    },
    ask: {
      title: 'ఫార్మ్‌సాథిని అడగండి',
      subtitle: 'పంటలు, వాతావరణం, పురుగులు, ఎరువులు లేదా సాగు గురించి ఏ ప్రశ్నైనా అడగండి.',
      inputPlaceholder: 'మీ వ్యవసాయ ప్రశ్నను ఇక్కడ రాయండి...',
      speak: 'మాట్లాడండి',
      listening: 'వింటున్నాం... స్పష్టంగా మాట్లాడండి',
      stop: 'ఆపండి',
      send: 'పంపండి',
      commonQuestions: 'రైతులు తరచుగా అడిగే ప్రశ్నలు',
      q1: 'ఈ రోజు మా పొలంలో వర్షం పడుతుందా?',
      q2: 'వరిలో అగ్గి తెగులును ఎలా నివారించాలి?',
      q3: 'పత్తి పంటకు ఎరువుల మోతాదు ఏమిటి?',
      q4: 'పంటకు నీరు ఎప్పుడు పెట్టాలి?',
      consulting: 'ఫార్మ్‌సాథి సలహా కేంద్రంతో సంప్రదిస్తున్నాం...',
      loginRequired: 'వ్యవసాయ సలహాలు పొందడానికి దయచేసి లాగిన్ అవ్వండి.',
      loginToAsk: 'ప్రశ్నించడానికి లాగిన్ అవ్వండి',
      submitQuestion: 'ఫార్మ్‌సాథిని అడగండి',
      submitWithPhoto: 'ప్రశ్న మరియు ఫోటో పంపండి',
      retry: 'మళ్లీ ప్రయత్నించండి',
      errorTitle: 'సలహా సమాచారం',
    },
    myCrops: {
      title: 'నా పంటలు',
      subtitle: 'మీ పంటల వివరాలు, నేల సిఫార్సులు మరియు దశలను పర్యవేక్షించండి.',
      addCrop: 'పంటను జోడించండి',
      cropName: 'పంట పేరు',
      cropNamePlaceholder: 'పంట పేరు (ఉదా: వరి, పత్తి)',
      emptyTitle: 'ఇంకా ఏ పంటలు జోడించలేదు.',
      emptySubtitle:
        'మీ పంటలను నమోదు చేసుకొని వాటి సంరక్షణ మరియు పెరుగుదలను గమనించండి.',
      findCropButton: 'సిఫార్సు చేసిన పంటను కనుగొనండి',
      activeCrops: 'సాగులో ఉన్న పంటలు',
      plantedOn: 'నాటిన తేదీ',
      recommendedConditions: 'అనుకూల పరిస్థితులు',
    },
    history: {
      title: 'వ్యవసాయ చరిత్ర',
      subtitle: 'గతంలో చేసిన పంట సిఫార్సులు, వ్యాధి పరీక్షలు మరియు సలహా వివరాలు.',
      tabAll: 'మొత్తం చరిత్ర',
      tabCrops: 'పంట సిఫార్సులు',
      tabDiagnosis: 'వ్యాధి నిర్ధారణలు',
      tabAdvisory: 'వ్యవసాయ సలహాలు',
      emptyTitle: 'ఇంకా ఎలాంటి చరిత్ర లేదు.',
      emptySubtitle: 'మీరు అడిగిన ప్రశ్నలు మరియు తెగులు పరీక్షలు ఇక్కడ భద్రపరచబడతాయి.',
    },
    common: {
      loading: 'లోడ్ అవుతోంది...',
      save: 'భద్రపరచు',
      cancel: 'రద్దు చేయి',
      close: 'మూసివేయి',
      error: 'లోపం సంభవించింది',
      tryAgain: 'మళ్లీ ప్రయత్నించండి',
      guestMode: 'అతిథి మోడ్',
      saved: 'చరిత్రలో భద్రపరచబడింది',
      searchLocation: 'గ్రామం లేదా నగరం వెతకండి',
      useCurrentLocation: 'GPS లొకేషన్ ఉపయోగించండి',
      enterCityName: 'ఊరు లేదా జిల్లా పేరు రాయండి...',
      search: 'వెతకండి',
      locationNotFound: 'లొకేషన్ కనుగొనబడలేదు. మళ్లీ ప్రయత్నించండి.',
      voice_input: 'వాయిస్ ఇన్‌పుట్',
      speak_placeholder: 'ప్రశ్న మాట్లాడండి',
      camera_upload: 'ఫోటో జోడించండి',
      disease_detection: 'వ్యాధి నిర్ధారణ',
      crop_recommendation: 'పంట సిఫార్సు',
      advisory: 'వ్యవసాయ సలహా',
      recent_activity: 'ఇటీవలి వ్యవసాయ వివరాలు',
      no_activity: 'ఇటీవలి వివరాలు ఏవీ లేవు.',
      no_activity_desc: 'మీరు అడిగిన ప్రశ్నలు, తెగులు గుర్తింపులు ఇక్కడ కనిపిస్తాయి.',
      ask_new_question: 'కొత్త సెషన్',
      ask_question: 'ప్రశ్న అడగండి',
      queries: 'ప్రశ్నలు',
      type_placeholder: 'మీ వ్యవసాయ ప్రశ్నను ఇక్కడ రాయండి...',
      foliage_context: 'ఆకు స్థితి',
      crop_health: 'పంట ఆరోగ్యం',
      all: 'మొత్తం వివరాలు',
      back: 'వెనుకకు',
      listening: 'వింటున్నాం...',
      reverse_geocoding_failed: 'ప్రాంతం పేరు గుర్తించలేకపోయాము. దయచేసి మాన్యువల్‌గా ఎంచుకోండి.',
    },
  },

  hi: {
    nav: {
      brand: 'फार्मसाथी',
      home: 'होम',
      ask: 'पूछें',
      myCrops: 'मेरी फसलें',
      diagnosis: 'रोग पहचान',
      cropRecommendation: 'फसल सिफ़ारिश',
      history: 'इतिहास',
      profile: 'प्रोफ़ाइल',
      login: 'लॉग इन',
      logout: 'लॉग आउट',
      selectLocation: 'स्थान चुनें',
      detectLocation: 'GPS स्थान खोजें',
    },
    welcome: {
      title: 'फार्मसाथी में आपका स्वागत है',
      tagline: 'आपका डिजिटल कृषि सहायक',
      description:
        'फार्मसाथी भारतीय किसानों को फसल सिफ़ारिश, रोग निदान, मौसम पूर्वानुमान और विशेषज्ञ कृषि सलाह प्रदान करता है।',
      selectLanguagePrompt: 'अपनी भाषा चुनें',
      continueButton: 'आगे बढ़ें',
      cropRec: 'स्मार्ट फसल सिफ़ारिश',
      cropRecDesc: 'मिट्टी के पोषक तत्वों और मौसम के अनुसार सर्वोत्तम फसल चुनें।',
      disease: 'त्वरित रोग पहचान',
      diseaseDesc: 'पत्ती की फोटो लेकर रोग पहचानें और जैविक समाधान पाएं।',
      weather: 'सटीक कृषि मौसम',
      weatherDesc: 'लाइव बारिश का अनुमान, तापमान और स्थानीय कृषि सलाह।',
    },
    permissions: {
      title: 'फार्मसाथी सेटअप',
      subtitle: 'फार्मसाथी को बेहतर बनाने के लिए आवश्यक अनुमतियां चुनें।',
      optionalBadge: 'वैकल्पिक',
      locationTitle: 'स्थान (लोकेशन)',
      locationDesc: 'स्थानीय मौसम, बारिश और कृषि परामर्श के लिए।',
      locationDetecting: 'स्थान खोजा जा रहा है...',
      locationEnabled: 'स्थान मिल गया',
      locationAllow: 'वर्तमान स्थान चुनें',
      locationManualOption: 'स्थान स्वयं चुनें',
      locationUnavailable: 'स्थान उपलब्ध नहीं है। आप जिला स्वयं चुन सकते हैं।',
      locationContext: 'स्थानीय मौसम और संदर्भ',
      cameraTitle: 'कैमरा',
      cameraDesc: 'फसल की बीमारी की पहचान के लिए पत्ती की फोटो खींचें।',
      cameraReady: 'कैमरा तैयार है',
      cameraContext: 'रोग निदान फोटो',
      cameraEnabled: 'कैमरा चालू है',
      cameraAllow: 'कैमरे की अनुमति दें',
      cameraFallback: 'गैलरी से फोटो अपलोड कर सकते हैं',
      micTitle: 'माइक (माइक्रोफोन)',
      micDesc: 'बोलकर अपनी भाषा में खेती से जुड़े सवाल पूछें।',
      micReady: 'माइक तैयार है',
      micContext: 'अपनी भाषा में बोलकर पूछें',
      micEnabled: 'माइक चालू है',
      micAllow: 'माइक की अनुमति दें',
      micFallback: 'टाइप करके भी सवाल पूछ सकते हैं',
      optionalNotice:
        'अनुमतियां वैकल्पिक हैं। आप कभी भी फोटो अपलोड और मैनुअल लोकेशन चुन सकते हैं।',
      skipForNow: 'अभी छोड़ें',
      continue: 'जारी रखें',
    },
    dashboard: {
      greeting: 'नमस्ते, किसान मित्र',
      heroTitle: 'आपका स्मार्ट कृषि साथी',
      heroSubtitle:
        'आज का मौसम, फसल स्वास्थ्य, उपयुक्त फसल या खेती से जुड़ा कोई भी सवाल पूछें।',
      askPlaceholder: 'फसल, बारिश, खाद या मिट्टी के बारे में कुछ भी पूछें...',
      askButton: 'पूछें',
      quickActions: 'प्रमुख कृषि सेवाएं',
      actionCropRec: 'सर्वोत्तम फसल खोजें',
      actionCropRecDesc: 'मिट्टी आधारित AI फसल सिफ़ारिश',
      actionDiagnosis: 'रोग की पहचान करें',
      actionDiagnosisDesc: 'पत्ती की फोटो से रोग व उपचार जानें',
      actionAsk: 'कृषि सलाहकार से पूछें',
      actionAskDesc: 'खेती के सवालों के त्वरित उत्तर',
      actionMyCrops: 'मेरी फसलें',
      actionMyCropsDesc: 'फसलों की बढ़वार और देखरेख दर्ज करें',
      recentActivity: 'हाल की गतिविधियां',
      noActivity: 'अभी तक कोई गतिविधि नहीं है।',
      noActivityDesc:
        'सवाल पूछने, रोग निदान या फसल सिफ़ारिश के बाद आपका इतिहास यहाँ दिखेगा।',
      viewAll: 'पूरा इतिहास देखें',
    },
    weather: {
      cardTitle: 'आज का खेत का मौसम',
      temperature: 'तापमान',
      humidity: 'हवा में नमी',
      rainfall: 'वर्षा का अनुमान',
      wind: 'हवा की गति',
      forecast: '7 दिनों का मौसम पूर्वानुमान',
      loading: 'मौसम की जानकारी ला रहे हैं...',
      unavailable: 'मौसम की जानकारी उपलब्ध नहीं है।',
      selectLocationPrompt: 'मौसम देखने के लिए अपना स्थान चुनें।',
    },
    cropRec: {
      title: 'अपने खेत के लिए सबसे उपयुक्त फसल चुनें',
      subtitle:
        'मिट्टी के पोषक तत्वों (N-P-K) और जलवायु के आधार पर सटीक फसल की जानकारी पाएं।',
      soilNutrients: 'मिट्टी के पोषक तत्व (N - P - K)',
      nitrogen: 'नाइट्रोजन (N) - किग्रा/हेक्टेयर',
      nitrogenPlaceholder: 'नाइट्रोजन दर्ज करें (उदा. 20 - 140)',
      phosphorus: 'फास्फोरस (P) - किग्रा/हेक्टेयर',
      phosphorusPlaceholder: 'फास्फोरस दर्ज करें (उदा. 10 - 100)',
      potassium: 'पोटाश (K) - किग्रा/हेक्टेयर',
      potassiumPlaceholder: 'पोटाश दर्ज करें (उदा. 10 - 100)',
      climateConditions: 'जलवायु एवं मिट्टी की स्थिति',
      temperature: 'तापमान (°C)',
      temperaturePlaceholder: 'तापमान दर्ज करें (15 - 40)',
      humidity: 'सापेक्ष आर्द्रता (%)',
      humidityPlaceholder: 'नमी दर्ज करें (30 - 90)',
      ph: 'मृदा pH (0 - 14)',
      phPlaceholder: 'pH मान दर्ज करें (उदा. 5.5 - 7.5)',
      rainfall: 'वार्षिक वर्षा (मिमी)',
      rainfallPlaceholder: 'वर्षा दर्ज करें (उदा. 100 - 300)',
      fillFromWeather: 'वर्तमान मौसम से तापमान और नमी भरें',
      calculateButton: 'अनुशंसित फसल की गणना करें',
      calculating: 'मिट्टी व जलवायु का विश्लेषण जारी है...',
      resultTitle: 'अनुशंसित फसल',
      whyThisCrop: 'यह फसल क्यों उपयुक्त है?',
      whyDesc:
        'आपकी मिट्टी के पोषक तत्वों, pH और जलवायु के अनुसार यह फसल अधिकतम उत्पादन देने में सक्षम है।',
      inputSummary: 'दर्ज किए गए आंकड़े',
      checkAnother: 'दूसरे खेत की जांच करें',
    },
    disease: {
      title: 'फसल रोग पहचान',
      subtitle:
        'त्वरित रोग पहचान और जैविक उपचार के लिए प्रभावित पत्ती की फोटो लें या अपलोड करें।',
      takePhoto: 'कैमरे से फोटो लें',
      uploadPhoto: 'गैलरी से अपलोड करें',
      changePhoto: 'फोटो बदलें',
      diagnoseButton: 'फसल के स्वास्थ्य की जांच करें',
      diagnosing: 'पत्ती की जांच हो रही है...',
      resultTitle: 'रोग पहचान परिणाम',
      cropDetected: 'फसल',
      conditionDetected: 'रोग / स्थिति',
      confidenceLabel: 'सटीकता',
      healthyFoliage: 'स्वस्थ पत्तियां',
      diseaseDetected: 'रोग की पहचान हुई',
      managementGuidance: 'रोकथाम एवं कृषि उपाय',
      culturalPractices: 'कृषि पद्धतियां',
      sanitation: 'खेत की स्वच्छता',
      prevention: 'निवारक उपाय',
      disclaimer:
        'रासायनिक दवाओं के छिड़काव के लिए अपने नजदीकी कृषि विज्ञान केंद्र (KVK) से सलाह लें।',
      scanAnother: 'दूसरी फसल की जांच करें',
      emptyUploadPrompt: 'कृपया पहले फसल की पत्ती की फोटो चुनें।',
      unsuitableTitle: 'यह छवि फसल रोग पहचान के लिए उपयुक्त नहीं है',
      unsuitablePrompt:
        'कृपया प्रभावित फसल की पत्ती की स्पष्ट क्लोज-अप तस्वीर लें या अपलोड करें।',
      retakePhoto: 'फिर से फोटो लें',
    },
    ask: {
      title: 'फार्मसाथी से पूछें',
      subtitle: 'अपनी फसल, मौसम, बीमारी, खाद या पानी से जुड़ा कोई भी सवाल पूछें।',
      inputPlaceholder: 'अपना सवाल यहाँ लिखें...',
      speak: 'बोलें',
      listening: 'सुन रहे हैं... बोलिए',
      stop: 'रोकें',
      send: 'भेजें',
      commonQuestions: 'अक्सर पूछे जाने वाले सवाल',
      q1: 'क्या आज मेरे खेत में बारिश होगी?',
      q2: 'धान को झुलसा रोग से कैसे बचाएं?',
      q3: 'गेहूं की फसल के लिए सही खाद प्रबंधन क्या है?',
      q4: 'फसलों की सिंचाई कब करनी चाहिए?',
      consulting: 'फार्मसाथी सलाह इंजन से परामर्श ले रहे हैं...',
      loginRequired: 'कृषि सलाह प्राप्त करने और सवाल पूछने के लिए कृपया साइन इन करें।',
      loginToAsk: 'सवाल पूछने के लिए साइन इन करें',
      submitQuestion: 'फार्मसाथी से पूछें',
      submitWithPhoto: 'सवाल और फोटो भेजें',
      retry: 'पुनः प्रयास करें',
      errorTitle: 'सलाह सूचना',
    },
    myCrops: {
      title: 'मेरी फसलें',
      subtitle: 'अपनी फसलों, मिट्टी की सिफारिशों और विकास की निगरानी करें।',
      addCrop: 'फसल जोड़ें',
      cropName: 'फसल का नाम',
      cropNamePlaceholder: 'फसल का नाम दर्ज करें (उदा. धान, कपास)',
      emptyTitle: 'अभी तक कोई फसल नहीं जोड़ी गई है।',
      emptySubtitle:
        'अपनी फसलों की देखभाल के लिए फसल सिफ़ारिश लें या अपनी मौजूदा फसल जोड़ें।',
      findCropButton: 'अनुशंसित फसल खोजें',
      activeCrops: 'सक्रिय फसलें',
      plantedOn: 'बुवाई की तारीख',
      recommendedConditions: 'अनुकूल मिट्टी की स्थिति',
    },
    history: {
      title: 'कृषि इतिहास',
      subtitle: 'अपनी पिछली फसल सिफ़ारिशें, रोग जांच और कृषि सलाह इतिहास देखें।',
      tabAll: 'सभी गतिविधियां',
      tabCrops: 'फसल सिफ़ारिशें',
      tabDiagnosis: 'रोग पहचान',
      tabAdvisory: 'कृषि परामर्श',
      emptyTitle: 'अभी तक कोई इतिहास नहीं है।',
      emptySubtitle: 'आपकी फसल सिफ़ारिशें, रोग जांच और पूछे गए सवाल यहाँ सुरक्षित रहेंगे।',
    },
    common: {
      loading: 'लोड हो रहा है...',
      save: 'सुरक्षित करें',
      cancel: 'रद्द करें',
      close: 'बंद करें',
      error: 'त्रुटि हुई',
      tryAgain: 'पुनः प्रयास करें',
      guestMode: 'अतिथि मोड',
      saved: 'इतिहास में सुरक्षित किया गया',
      searchLocation: 'शहर या गाँव खोजें',
      useCurrentLocation: 'GPS स्थान का उपयोग करें',
      enterCityName: 'शहर या ज़िले का नाम लिखें...',
      search: 'खोजें',
      locationNotFound: 'कोई स्थान नहीं मिला। कृपया दूसरा नाम खोजें।',
      voice_input: 'आवाज इनपुट',
      speak_placeholder: 'सवाल बोलें',
      camera_upload: 'फोटो जोड़ें',
      disease_detection: 'रोग पहचान',
      crop_recommendation: 'फसल सिफ़ारिश',
      advisory: 'कृषि सलाह',
      recent_activity: 'हाल की गतिविधियां',
      no_activity: 'अभी तक कोई गतिविधि नहीं है।',
      no_activity_desc: 'आपके सवाल और फसल जांच का विवरण यहाँ दिखाई देगा।',
      ask_new_question: 'नया सत्र',
      ask_question: 'सवाल पूछें',
      queries: 'सवाल',
      type_placeholder: 'अपना कृषि सवाल यहाँ लिखें...',
      foliage_context: 'पत्ती की स्थिति',
      crop_health: 'फसल स्वास्थ्य',
      all: 'सभी गतिविधियां',
      back: 'वापस',
      listening: 'सुन रहे हैं...',
      reverse_geocoding_failed: 'स्थान का नाम नहीं पहचाना जा सका। कृपया सूची से चुनें।',
    },
  },

  ta: {
    nav: {
      brand: 'பார்ம்சாதி',
      home: 'முகப்பு',
      ask: 'கேளுங்கள்',
      myCrops: 'என் பயிர்கள்',
      diagnosis: 'நோய் கண்டறிதல்',
      cropRecommendation: 'பயிர் பரிந்துரை',
      history: 'வரலாறு',
      profile: 'சுயவிவரம்',
      login: 'உள்நுழைவு',
      logout: 'வெளியேறு',
      selectLocation: 'இருப்பிடத்தைத் தேர்ந்தெடுக்கவும்',
      detectLocation: 'GPS இருப்பிடத்தைக் கண்டறியவும்',
    },
    welcome: {
      title: 'பார்ம்சாதிக்கு வரவேற்கிறோம்',
      tagline: 'உங்கள் டிஜிட்டல் விவசாயத் தோழன்',
      description:
        'பார்ம்சாதி விவசாயிகளுக்கு பயிர் பரிந்துரைகள், இலை நோய் கண்டறிதல், வானிலை மற்றும் வேளாண் ஆலோசனைகளை வழங்குகிறது.',
      selectLanguagePrompt: 'உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்',
      continueButton: 'பார்ம்சாதிக்குத் தொடரவும்',
      cropRec: 'ஸ்மார்ட் பயிர் பரிந்துரை',
      cropRecDesc: 'உங்கள் மண் ஊட்டச்சத்து மற்றும் காலநிலைக்கு ஏற்ற சிறந்த பயிரைக் கண்டறியவும்.',
      disease: 'உடனடி இலை நோய் கண்டறிதல்',
      diseaseDesc: 'இலைகளை ஸ்கேன் செய்து நோய்களைக் கண்டறிந்து இயற்கை மேலாண்மை ஆலோசனைகளைப் பெறுங்கள்.',
      weather: 'நம்பகமான பண்ணை வானிலை',
      weatherDesc: 'நேரடி மழைப்பொழிவு, வெப்பநிலை மற்றும் உள்ளூர் விவசாய ஆலோசனைகள்.',
    },
    permissions: {
      title: 'பார்ம்சாதி அமைப்பு',
      subtitle: 'பார்ம்சாதி பயன்படுத்த விரும்பும் அனுமதிகளைத் தேர்ந்தெடுக்கவும்.',
      optionalBadge: 'விருப்பத்திற்குரியது',
      locationTitle: 'இருப்பிடம்',
      locationDesc: 'உள்ளூர் வானிலை, மழை முன்னறிவிப்பு மற்றும் பகுதி விவசாய ஆலோசனைக்கு.',
      locationDetecting: 'இருப்பிடத்தைக் கண்டறிகிறது...',
      locationEnabled: 'இருப்பிடம் கண்டறியப்பட்டது',
      locationAllow: 'தற்போதைய இருப்பிடத்தைப் பயன்படுத்து',
      locationManualOption: 'இருப்பிடத்தை கைமுறையாகத் தேர்ந்தெடுக்கவும்',
      locationUnavailable: 'இருப்பிடம் கிடைக்கவில்லை. உங்கள் மாவட்டத்தை நீங்கள் தேர்வு செய்யலாம்.',
      locationContext: 'உள்ளூர் வானிலை மற்றும் சூழல்',
      cameraTitle: 'கேமரா',
      cameraDesc: 'நோய் கண்டறிதலுக்கு பாதிக்கப்பட்ட பயிர் இலைகளைப் படம் பிடிக்கவும்.',
      cameraReady: 'பயிர் புகைப்படத்திற்குத் தயார்',
      cameraContext: 'நோய் கண்டறிதல் புகைப்படங்கள்',
      cameraEnabled: 'கேமரா தயார்',
      cameraAllow: 'கேமராவை அனுமதிக்கவும்',
      cameraFallback: 'கேலரியிலிருந்து பதிவேற்றலாம்',
      micTitle: 'மைக்ரோஃபோன்',
      micDesc: 'உங்கள் விவசாயக் கேள்விகளை உங்கள் மொழியில் இயல்பாகப் பேசுங்கள்.',
      micReady: 'குரல் கேள்விகளுக்குத் தயார்',
      micContext: 'உங்கள் மொழியில் குரல் கேள்விகள்',
      micEnabled: 'மைக்ரோஃபோன் தயார்',
      micAllow: 'மைக்ரோஃபோனை அனுமதிக்கவும்',
      micFallback: 'தட்டச்சு மூலம் எப்போதும் கேட்கலாம்',
      optionalNotice:
        'அனுமதிகள் விருப்பத்திற்குரியவை. மறுக்கப்பட்டாலும் நீங்கள் புகைப்படங்களைப் பதிவேற்றி கேள்விகளைத் தட்டச்சு செய்யலாம்.',
      skipForNow: 'இப்போதைக்குத் தவிர்',
      continue: 'தொடரவும்',
    },
    dashboard: {
      greeting: 'வணக்கம், விவசாயி',
      heroTitle: 'உங்கள் அறிவார்ந்த விவசாயத் தோழன்',
      heroSubtitle:
        'இன்றைய வானிலை, பயிர் ஆரோக்கியம், சிறந்த பயிர் அல்லது ஏதேனும் வேளாண் கேள்விகளைக் கேளுங்கள்.',
      askPlaceholder: 'உங்கள் பயிர், மழை, உரம் அல்லது மண் பற்றி ஏதேனும் கேளுங்கள்...',
      askButton: 'கேளுங்கள்',
      quickActions: 'முக்கிய சேவைகள்',
      actionCropRec: 'சிறந்த பயிரைக் கண்டறியவும்',
      actionCropRecDesc: 'மண் பரிசோதனை அடிப்படையிலான AI பரிந்துரை',
      actionDiagnosis: 'பயிர் நோய் கண்டறிதல்',
      actionDiagnosisDesc: 'இலைகளை ஸ்கேன் செய்து தீர்வுகளைப் பெறுங்கள்',
      actionAsk: 'வேளாண் ஆலோசகரிடம் கேளுங்கள்',
      actionAskDesc: 'விவசாயக் கேள்விகளுக்கு உடனடி வழிகாட்டுதல்',
      actionMyCrops: 'என் பயிர்கள்',
      actionMyCropsDesc: 'உங்கள் பயிர் வளர்ச்சி மற்றும் பராமரிப்பைக் கண்காணியுங்கள்',
      recentActivity: 'சமீபத்திய விவசாய நடவடிக்கைகள்',
      noActivity: 'சமீபத்திய நடவடிக்கைகள் எதுவும் இல்லை.',
      noActivityDesc:
        'கேள்வி கேட்கவும், இலையை ஸ்கேன் செய்யவும் அல்லது பயிர் பரிந்துரை பெறவும்.',
      viewAll: 'முழு வரலாற்றைக் காண்க',
    },
    weather: {
      cardTitle: 'இன்றைய பண்ணை வானிலை',
      temperature: 'வெப்பநிலை',
      humidity: 'ஒப்பீட்டு ஈரப்பதம்',
      rainfall: 'மழைப்பொழிவு',
      wind: 'காற்றின் வேகம்',
      forecast: '7 நாள் வானிலை முன்னறிவிப்பு',
      loading: 'வானிலை தகவல் பெறப்படுகிறது...',
      unavailable: 'வானிலை தகவல் கிடைக்கவில்லை.',
      selectLocationPrompt: 'நேரடி வானிலையைக் காண உங்கள் இருப்பிடத்தைத் தேர்ந்தெடுக்கவும்.',
    },
    cropRec: {
      title: 'உங்கள் நிலத்திற்கான சிறந்த பயிரைக் கண்டறியவும்',
      subtitle:
        'மண் ஊட்டச்சத்துக்கள் மற்றும் காலநிலை விவரங்களை உள்ளிட்டு அறிவியல் பூர்வமான சிறந்த பயிரைப் பெறுங்கள்.',
      soilNutrients: 'மண் ஊட்டச்சத்துக்கள் (N - P - K)',
      nitrogen: 'நைட்ரஜன் (N) - கிலோ/ஹெக்',
      nitrogenPlaceholder: 'நைட்ரஜன் மதிப்பை உள்ளிடவும் (उदा. 20 - 140)',
      phosphorus: 'பாஸ்பரஸ் (P) - கிலோ/ஹெக்',
      phosphorusPlaceholder: 'பாஸ்பரஸ் மதிப்பை உள்ளிடவும் (उदा. 10 - 100)',
      potassium: 'பொட்டாசியம் (K) - கிலோ/ஹெக்',
      potassiumPlaceholder: 'பொட்டாசியம் மதிப்பை உள்ளிடவும் (उदा. 10 - 100)',
      climateConditions: 'காலநிலை மற்றும் மண் நிலை',
      temperature: 'வெப்பநிலை (°C)',
      temperaturePlaceholder: 'வெப்பநிலையை உள்ளிடவும் (15 - 40)',
      humidity: 'ஒப்பீட்டு ஈரப்பதம் (%)',
      humidityPlaceholder: 'ஈரப்பதத்தை உள்ளிடவும் (30 - 90)',
      ph: 'மண் pH (0 - 14)',
      phPlaceholder: 'pH மதிப்பை உள்ளிடவும் (5.5 - 7.5)',
      rainfall: 'வருடாந்திர மழைப்பொழிவு (மிமீ)',
      rainfallPlaceholder: 'மழைப்பொழிவை உள்ளிடவும் (100 - 300)',
      fillFromWeather: 'வானிலையிலிருந்து வெப்பநிலை மற்றும் ஈரப்பதத்தை நிரப்பவும்',
      calculateButton: 'பரிந்துரைக்கப்பட்ட பயிரைக் கணக்கிடுக',
      calculating: 'மண் மற்றும் காலநிலையை ஆராய்கிறது...',
      resultTitle: 'பரிந்துரைக்கப்பட்ட பயிர்',
      whyThisCrop: 'இந்த பயிர் ஏன் சிறந்தது?',
      whyDesc:
        'உங்கள் மண் ஊட்டச்சத்துக்கள், pH மற்றும் காலநிலையின் அடிப்படையில் இந்த பயிர் அதிக மகசூலைத் தரும்.',
      inputSummary: 'உள்ளீட்டு விவரங்கள்',
      checkAnother: 'மற்றொரு நிலத்தைச் சரிபார்க்கவும்',
    },
    disease: {
      title: 'பயிர் இலை நோய் கண்டறிதல்',
      subtitle:
        'நோய் கண்டறிதல் மற்றும் இயற்கை மேலாண்மை ஆலோசனைக்கு பாதிக்கப்பட்ட இலை புகைப்படத்தைப் பதிவேற்றவும்.',
      takePhoto: 'கேமரா மூலம் படம் எடுக்கவும்',
      uploadPhoto: 'கேலரியிலிருந்து பதிவேற்றவும்',
      changePhoto: 'படத்தை மாற்றவும்',
      diagnoseButton: 'பயிர் ஆரோக்கியத்தைக் கண்டறியவும்',
      diagnosing: 'இலை ஆரோக்கியத்தை ஆராய்கிறது...',
      resultTitle: 'நோய் கண்டறிதல் முடிவு',
      cropDetected: 'பயிர்',
      conditionDetected: 'கண்டறியப்பட்ட நிலை',
      confidenceLabel: 'நம்பகத்தன்மை',
      healthyFoliage: 'ஆரோக்கியமான இலைகள்',
      diseaseDetected: 'நோய் அறிகுறிகள் கண்டறியப்பட்டன',
      managementGuidance: 'வேளாண் மற்றும் இயற்கை பராமரிப்பு',
      culturalPractices: 'பயிற்சி முறைகள்',
      sanitation: 'வயல் தூய்மை',
      prevention: 'தடுப்பு நடவடிக்கைகள்',
      disclaimer:
        'இரசாயன தெளிப்புகளுக்கு உங்கள் உள்ளூர் வேளாண் அறிவியல் மையத்தை (KVK) அணுகவும்.',
      scanAnother: 'மற்றொரு இலையை ஸ்கேன் செய்யவும்',
      emptyUploadPrompt: 'தயவுசெய்து முதலில் இலை புகைப்படத்தைத் தேர்ந்தெடுக்கவும்.',
      unsuitableTitle: 'இந்த படம் பயிர் நோய் கண்டறிதலுக்கு ஏற்றதாக இல்லை',
      unsuitablePrompt:
        'பாதிக்கப்பட்ட பயிர் இலையின் தெளிவான நெருக்கமான புகைப்படத்தை எடுக்கவும் அல்லது பதிவேற்றவும்.',
      retakePhoto: 'மீண்டும் படம் எடுக்கவும்',
    },
    ask: {
      title: 'பார்ம்சாதியிடம் கேளுங்கள்',
      subtitle: 'பயிர்கள், வானிலை, பூச்சி மேலாண்மை அல்லது உரங்கள் பற்றி எந்தக் கேள்வியும் கேளுங்கள்.',
      inputPlaceholder: 'உங்கள் விவசாயக் கேள்வியை இங்கே தட்டச்சு செய்யவும்...',
      speak: 'பேசுங்கள்',
      listening: 'கேட்கிறது... தெளிவாகப் பேசுங்கள்',
      stop: 'நிறுத்து',
      send: 'அனுப்பு',
      commonQuestions: 'அடிக்கடி கேட்கப்படும் கேள்விகள்',
      q1: 'இன்று என் பண்ணையில் மழை பெய்யுமா?',
      q2: 'நெல் பயிரில் குலை நோயை எவ்வாறு கட்டுப்படுத்துவது?',
      q3: 'கோதுமைக்கு பரிந்துரைக்கப்படும் உர அட்டவணை என்ன?',
      q4: 'பயிர்களுக்கு எப்போது தண்ணீர் பாய்ச்ச வேண்டும்?',
      consulting: 'பார்ம்சாதி ஆலோசனை இயந்திரத்தைக் கலந்தாலோசிக்கிறது...',
      loginRequired: 'கேள்விகள் கேட்கவும் ஆலோசனை பெறவும் உள்நுழையவும்.',
      loginToAsk: 'கேட்க உள்நுழையவும்',
      submitQuestion: 'பார்ம்சாதியிடம் கேளுங்கள்',
      submitWithPhoto: 'கேள்வி மற்றும் புகைப்படத்தை அனுப்பவும்',
      retry: 'மீண்டும் முயற்சி செய்க',
      errorTitle: 'ஆலோசனை அறிவிப்பு',
    },
    myCrops: {
      title: 'என் பயிர்கள்',
      subtitle: 'உங்கள் பயிர்கள், மண் பரிந்துரைகள் மற்றும் வளர்ச்சி நிலைகளைக் கண்காணிக்கவும்.',
      addCrop: 'பயிரைச் சேர்க்கவும்',
      cropName: 'பயிர் பெயர்',
      cropNamePlaceholder: 'பயிர் பெயரை உள்ளிடவும் (उदा. நெல், பருத்தி)',
      emptyTitle: 'இன்னும் பயிர்கள் சேர்க்கப்படவில்லை.',
      emptySubtitle:
        'உங்கள் பயிர்களைப் பதிவு செய்து அவற்றின் வளர்ச்சியை இங்கே கண்காணிக்கவும்.',
      findCropButton: 'பரிந்துரைக்கப்பட்ட பயிரைக் கண்டறியவும்',
      activeCrops: 'நடப்பு பயிர்கள்',
      plantedOn: 'பயிரிடப்பட்ட தேதி',
      recommendedConditions: 'பரிந்துரைக்கப்பட்ட சூழல்கள்',
    },
    history: {
      title: 'பண்ணை வரலாறு',
      subtitle: 'உங்கள் கடந்தகால பயிர் பரிந்துரைகள், நோய் ஸ்கேன்கள் மற்றும் ஆலோசனைகளைக் காண்க.',
      tabAll: 'அனைத்து நடவடிக்கைகள்',
      tabCrops: 'பயிர் பரிந்துரைகள்',
      tabDiagnosis: 'நோய் கண்டறிதல்கள்',
      tabAdvisory: 'வேளாண் ஆலோசனைகள்',
      emptyTitle: 'நடவடிக்கைகள் எதுவும் இல்லை.',
      emptySubtitle: 'உங்கள் கேள்விகள் மற்றும் நோய் ஸ்கேன்கள் இங்கே சேமிக்கப்படும்.',
    },
    common: {
      loading: 'ஏற்றுகிறது...',
      save: 'சேமி',
      cancel: 'ரத்து செய்',
      close: 'மூடு',
      error: 'பிழை ஏற்பட்டது',
      tryAgain: 'மீண்டும் முயற்சிக்கவும்',
      guestMode: 'விருந்தினர் முறை',
      saved: 'வரலாற்றில் சேமிக்கப்பட்டது',
      searchLocation: 'நகரம் அல்லது கிராமத்தைத் தேடுங்கள்',
      useCurrentLocation: 'GPS இருப்பிடத்தைப் பயன்படுத்து',
      enterCityName: 'நகரம் அல்லது மாவட்டப் பெயரை உள்ளிடவும்...',
      search: 'தேடு',
      locationNotFound: 'பொருத்தமான இருப்பிடம் கிடைக்கவில்லை.',
      voice_input: 'குரல் உள்ளீடு',
      speak_placeholder: 'கேள்வியைப் பேசுங்கள்',
      camera_upload: 'படம் சேர்க்க',
      disease_detection: 'நோய் கண்டறிதல்',
      crop_recommendation: 'பயிர் பரிந்துரை',
      advisory: 'வேளாண் ஆலோசனை',
      recent_activity: 'சமீபத்திய நடவடிக்கைகள்',
      no_activity: 'நடவடிக்கைகள் எதுவும் இல்லை',
      no_activity_desc: 'உங்கள் கேள்விகள் மற்றும் நோய் கண்டறிதல்கள் இங்கே தோன்றும்.',
      ask_new_question: 'புதிய அமர்வு',
      ask_question: 'கேள்வி கேளுங்கள்',
      queries: 'கேள்விகள்',
      type_placeholder: 'உங்கள் விவசாயக் கேள்வியை இங்கே எழுதவும்...',
      foliage_context: 'இலை சூழல்',
      crop_health: 'பயிர் நலம்',
      all: 'அனைத்து நடவடிக்கைகள்',
      back: 'பின்செல்',
      listening: 'கேட்கிறது...',
      reverse_geocoding_failed: 'நகரத்தின் பெயரைத் தீர்மானிக்க முடியவில்லை. கைமுறையாகத் தேர்ந்தெடுக்கவும்.',
    },
  },

  kn: {
    nav: {
      brand: 'ಫಾರ್ಮ್‌ಸಾಥಿ',
      home: 'ಮುಖಪುಟ',
      ask: 'ಕೇಳಿ',
      myCrops: 'ನನ್ನ ಬೆಳೆಗಳು',
      diagnosis: 'ರೋಗ ಪತ್ತೆ',
      cropRecommendation: 'ಬೆಳೆ ಶಿಫಾರಸು',
      history: 'ಇತಿಹಾಸ',
      profile: 'ಪ್ರೊಫೈಲ್',
      login: 'ಲಾಗಿನ್',
      logout: 'ಲಾಗ್‌ಔಟ್',
      selectLocation: 'ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
      detectLocation: 'GPS ಸ್ಥಳ ಪತ್ತೆಹಚ್ಚಿ',
    },
    welcome: {
      title: 'ಫಾರ್ಮ್‌ಸಾಥಿಗೆ ಸುಸ್ವಾಗತ',
      tagline: 'ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಕೃಷಿ ಒಡನಾಡಿ',
      description:
        'ಫಾರ್ಮ್‌ಸಾಥಿ ರೈತರಿಗೆ ನಿಖರವಾದ ಬೆಳೆ ಶಿಫಾರಸುಗಳು, ರೋಗ ಪತ್ತೆ, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಮತ್ತು ತಜ್ಞರ ಕೃಷಿ ಸಲಹೆಗಳನ್ನು ನೀಡುತ್ತದೆ.',
      selectLanguagePrompt: 'ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ',
      continueButton: 'ಫಾರ್ಮ್‌ಸಾಥಿಗೆ ಮುಂದುವರಿಯಿರಿ',
      cropRec: 'ಸ್ಮಾರ್ಟ್ ಬೆಳೆ ಶಿಫಾರಸು',
      cropRecDesc: 'ನಿಮ್ಮ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಸೂಕ್ತವಾದ ಬೆಳೆಯನ್ನು ಕಂಡುಕೊಳ್ಳಿ.',
      disease: 'ತಕ್ಷಣದ ಎಲೆ ರೋಗ ಪತ್ತೆ',
      diseaseDesc: 'ಎಲೆಗಳನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ ರೋಗಗಳನ್ನು ಪತ್ತೆಹಚ್ಚಿ ಮತ್ತು ನೈಸರ್ಗಿಕ ನಿರ್ವಹಣಾ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಿರಿ.',
      weather: 'ದೃಢೀಕೃತ ಕೃಷಿ ಹವಾಮಾನ',
      weatherDesc: 'ನೈಜ-ಸಮಯದ ಮಳೆ ಮುನ್ಸೂಚನೆ, ತಾಪಮಾನ ಮತ್ತು ಸ್ಥಳೀಯ ಕೃಷಿ ಸಲಹೆಗಳು.',
    },
    permissions: {
      title: 'ಫಾರ್ಮ್‌ಸಾಥಿ ಸೆಟಪ್',
      subtitle: 'ಫಾರ್ಮ್‌ಸಾಥಿ ಬಳಸಲು ನೀವು ಬಯಸುವ ಅನುಮತಿಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ.',
      optionalBadge: 'ಐಚ್ಛಿಕ',
      locationTitle: 'ಸ್ಥಳ (ಲೊಕೇಶನ್)',
      locationDesc: 'ಸ್ಥಳೀಯ ಹವಾಮಾನ, ಮಳೆ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಕೃಷಿ ಸಲಹೆಗಾಗಿ.',
      locationDetecting: 'ಸ್ಥಳವನ್ನು ಪತ್ತೆಹಚ್ಚಲಾಗುತ್ತಿದೆ...',
      locationEnabled: 'ಸ್ಥಳ ಪತ್ತೆಯಾಗಿದೆ',
      locationAllow: 'ಪ್ರಸ್ತುತ ಸ್ಥಳ ಬಳಸಿ',
      locationManualOption: 'ಸ್ಥಳವನ್ನು ಹಸ್ತಚಾಲಿತವಾಗಿ ಆಯ್ಕೆಮಾಡಿ',
      locationUnavailable: 'ಸ್ಥಳ ಲಭ್ಯವಿಲ್ಲ. ನಿಮ್ಮ ಜಿಲ್ಲೆಯನ್ನು ನೀವು ಹಸ್ತಚಾಲಿತವಾಗಿ ಆಯ್ಕೆಮಾಡಬಹುದು.',
      locationContext: 'ಸ್ಥಳೀಯ ಹವಾಮಾನ ಮತ್ತು ಮಾಹಿತಿ',
      cameraTitle: 'ಕ್ಯಾಮೆರಾ',
      cameraDesc: 'ರೋಗ ಪತ್ತೆಗಾಗಿ ಬಾಧಿತ ಬೆಳೆ ಎಲೆಗಳ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.',
      cameraReady: 'ಬೆಳೆ ಫೋಟೋಗಳಿಗೆ ಸಿದ್ಧವಾಗಿದೆ',
      cameraContext: 'ಬೆಳೆ ರೋಗ ಪತ್ತೆ ಫೋಟೋಗಳು',
      cameraEnabled: 'ಕ್ಯಾಮೆರಾ ಸಿದ್ಧವಾಗಿದೆ',
      cameraAllow: 'ಕ್ಯಾಮೆರಾವನ್ನು ಅನುಮತಿಸಿ',
      cameraFallback: 'ಗ್ಯಾಲರಿಯಿಂದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಬಹುದು',
      micTitle: 'ಮೈಕ್ರೊಫೋನ್',
      micDesc: 'ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಸರಳವಾಗಿ ಮಾತನಾಡಿ.',
      micReady: 'ಧ್ವನಿ ಪ್ರಶ್ನೆಗಳಿಗೆ ಸಿದ್ಧವಾಗಿದೆ',
      micContext: 'ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಧ್ವನಿ ಪ್ರಶ್ನೆಗಳು',
      micEnabled: 'ಮೈಕ್ರೊಫೋನ್ ಸಿದ್ಧವಾಗಿದೆ',
      micAllow: 'ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿಸಿ',
      micFallback: 'ಟೈಪ್ ಮಾಡುವ ಮೂಲಕ ಯಾವಾಗಲೂ ಕೇಳಬಹುದು',
      optionalNotice:
        'ಅನುಮತಿಗಳು ಐಚ್ಛಿಕವಾಗಿವೆ. ಅನುಮತಿಸದಿದ್ದರೂ ನೀವು ಫೋಟೋಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಬಹುದು ಮತ್ತು ಪ್ರಶ್ನೆಗಳನ್ನು ಟೈಪ್ ಮಾಡಬಹುದು.',
      skipForNow: 'ಈಗ ಬಿಟ್ಟುಬಿಡಿ',
      continue: 'ಮುಂದುವರಿಯಿರಿ',
    },
    dashboard: {
      greeting: 'ನಮಸ್ಕಾರ, ರೈತರೇ',
      heroTitle: 'ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಕೃಷಿ ಒಡನಾಡಿ',
      heroSubtitle:
        'ಇಂದಿನ ಹವಾಮಾನ, ಬೆಳೆ ಆರೋಗ್ಯ, ಉತ್ತಮ ಬೆಳೆ ಅಥವಾ ಯಾವುದೇ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ.',
      askPlaceholder: 'ನಿಮ್ಮ ಬೆಳೆ, ಮಳೆ, ಗೊಬ್ಬರ ಅಥವಾ ಮಣ್ಣಿನ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ...',
      askButton: 'ಕೇಳಿ',
      quickActions: 'ಪ್ರಮುಖ ಕೃಷಿ ಸೇವೆಗಳು',
      actionCropRec: 'ಉತ್ತಮ ಬೆಳೆ ಹುಡುಕಿ',
      actionCropRecDesc: 'ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಯ ಆಧಾರಿತ AI ಶಿಫಾರಸು',
      actionDiagnosis: 'ಬೆಳೆ ರೋಗ ಪತ್ತೆ',
      actionDiagnosisDesc: 'ಎಲೆ ಫೋಟೋ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ ಪರಿಹಾರಗಳನ್ನು ಪಡೆಯಿರಿ',
      actionAsk: 'ಕೃಷಿ ಸಲಹೆಗಾರರನ್ನು ಕೇಳಿ',
      actionAskDesc: 'ಕೃಷಿ ಪ್ರಶ್ನೆಗಳಿಗೆ ತ್ವರಿತ ಮಾರ್ಗದರ್ಶನ',
      actionMyCrops: 'ನನ್ನ ಬೆಳೆಗಳು',
      actionMyCropsDesc: 'ನಿಮ್ಮ ಬೆಳೆಗಳ ಬೆಳವಣಿಗೆಯನ್ನು ಗಮನಿಸಿ',
      recentActivity: 'ಇತ್ತೀಚಿನ ಕೃಷಿ ಚಟುವಟಿಕೆಗಳು',
      noActivity: 'ಯಾವುದೇ ಇತ್ತೀಚಿನ ಚಟುವಟಿಕೆಗಳಿಲ್ಲ.',
      noActivityDesc:
        'ಪ್ರಶ್ನೆ ಕೇಳಿ, ಎಲೆ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ ಅಥವಾ ಬೆಳೆ ಶಿಫಾರಸು ಪಡೆದು ನಿಮ್ಮ ಇತಿಹಾಸವನ್ನು ಇಲ್ಲಿ ನೋಡಿ.',
      viewAll: 'ಪೂರ್ಣ ಇತಿಹಾಸ ನೋಡಿ',
    },
    weather: {
      cardTitle: 'ಇಂದಿನ ಕೃಷಿ ಹವಾಮಾನ',
      temperature: 'ತಾಪಮಾನ',
      humidity: 'ತೇವಾಂಶ',
      rainfall: 'ಮಳೆ ಪ್ರಮಾಣ',
      wind: 'ಗಾಳಿಯ ವೇಗ',
      forecast: '7 ದಿನಗಳ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ',
      loading: 'ಹವಾಮಾನ ಮಾಹಿತಿ ಪಡೆಯಲಾಗುತ್ತಿದೆ...',
      unavailable: 'ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.',
      selectLocationPrompt: 'ನೇರ ಹವಾಮಾನವನ್ನು ನೋಡಲು ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಆಯ್ಕೆಮಾಡಿ.',
    },
    cropRec: {
      title: 'ನಿಮ್ಮ ಜಮೀನಿಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಯನ್ನು ಕಂಡುಕೊಳ್ಳಿ',
      subtitle:
        'ವೈಜ್ಞಾನಿಕವಾಗಿ ಅತ್ಯುತ್ತಮ ಬೆಳೆಯನ್ನು ಲೆಕ್ಕಾಚಾರ ಮಾಡಲು ನಿಮ್ಮ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು ಮತ್ತು ಹವಾಮಾನವನ್ನು ನಮೂದಿಸಿ.',
      soilNutrients: 'ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು (N - P - K)',
      nitrogen: 'ಸಾರಜನಕ (N) - ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
      nitrogenPlaceholder: 'ಸಾರಜನಕ ಮೌಲ್ಯ (ಉದಾ: 20 - 140)',
      phosphorus: 'ರಂಜಕ (P) - ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
      phosphorusPlaceholder: 'ರಂಜಕ ಮೌಲ್ಯ (ಉದಾ: 10 - 100)',
      potassium: 'ಪೊಟ್ಯಾಶ್ (K) - ಕೆಜಿ/ಹೆಕ್ಟೇರ್',
      potassiumPlaceholder: 'ಪೊಟ್ಯಾಶ್ ಮೌಲ್ಯ (ಉದಾ: 10 - 100)',
      climateConditions: 'ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ಸ್ಥಿತಿ',
      temperature: 'ತಾಪಮಾನ (°C)',
      temperaturePlaceholder: 'ತಾಪಮಾನ ನಮೂದಿಸಿ (15 - 40)',
      humidity: 'ತೇವಾಂಶ (%)',
      humidityPlaceholder: 'ತೇವಾಂಶ ನಮೂದಿಸಿ (30 - 90)',
      ph: 'ಮಣ್ಣಿನ pH (0 - 14)',
      phPlaceholder: 'pH ಮೌಲ್ಯ (ಉದಾ: 5.5 - 7.5)',
      rainfall: 'ವಾರ್ಷಿಕ ಮಳೆ (ಮಿಮೀ)',
      rainfallPlaceholder: 'ಮಳೆ ಪ್ರಮಾಣ (ಉದಾ: 100 - 300)',
      fillFromWeather: 'ಪ್ರಸ್ತುತ ಹವಾಮಾನದಿಂದ ತಾಪಮಾನ ಮತ್ತು ತೇವಾಂಶ ಭರ್ತಿ ಮಾಡಿ',
      calculateButton: 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಯನ್ನು ಲೆಕ್ಕಹಾಕಿ',
      calculating: 'ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನವನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...',
      resultTitle: 'ಶಿಫಾರಸು ಮಾಡಲಾದ ಬೆಳೆ',
      whyThisCrop: 'ಈ ಬೆಳೆ ಏಕೆ ಸೂಕ್ತ?',
      whyDesc:
        'ನೀವು ನಮೂದಿಸಿದ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು ಮತ್ತು ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳ ಆಧಾರದ ಮೇಲೆ ಈ ಬೆಳೆ ಗರಿಷ್ಠ ಇಳುವರಿ ನೀಡುತ್ತದೆ.',
      inputSummary: 'ನಮೂದಿಸಿದ ವಿವರಗಳು',
      checkAnother: 'ಮತ್ತೊಂದು ಜಮೀನು ಪರಿಶೀಲಿಸಿ',
    },
    disease: {
      title: 'ಬೆಳೆ ಎಲೆ ರೋಗ ಪತ್ತೆ',
      subtitle:
        'ತ್ವರಿತ ರೋಗ ಪತ್ತೆ ಮತ್ತು ಸಾವಯವ ನಿರ್ವಹಣಾ ಸಲಹೆಗಾಗಿ ಬಾಧಿತ ಎಲೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ ಅಥವಾ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.',
      takePhoto: 'ಕ್ಯಾಮೆರಾದಿಂದ ಫೋಟೋ ತೆಗೆಯಿರಿ',
      uploadPhoto: 'ಗ್ಯಾಲರಿಯಿಂದ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
      changePhoto: 'ಫೋಟೋ ಬದಲಾಯಿಸಿ',
      diagnoseButton: 'ಬೆಳೆ ಆರೋಗ್ಯ ಪರೀಕ್ಷಿಸಿ',
      diagnosing: 'ಎಲೆಯ ಆರೋಗ್ಯ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...',
      resultTitle: 'ರೋಗ ಪತ್ತೆ ಫಲಿತಾಂಶ',
      cropDetected: 'ಬೆಳೆ',
      conditionDetected: 'ಪತ್ತೆಯಾದ ರೋಗ / ಸ್ಥಿತಿ',
      confidenceLabel: 'ನಿಖರತೆ',
      healthyFoliage: 'ಆರೋಗ್ಯಕರ ಎಲೆಗಳು',
      diseaseDetected: 'ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ',
      managementGuidance: 'ಕೃಷಿ ಮತ್ತು ಸಾವಯವ ನಿರ್ವಹಣೆ',
      culturalPractices: 'ಕೃಷಿ ಪದ್ಧತಿಗಳು',
      sanitation: 'ಜಮೀನಿನ ಸ್ವಚ್ಛತೆ',
      prevention: 'ಮುನ್ನೆಚ್ಚರಿಕಾ ಕ್ರಮಗಳು',
      disclaimer:
        'ರಾಸಾಯನಿಕ ಔಷಧಿ ಸಿಂಪಡಣೆಗಾಗಿ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ.',
      scanAnother: 'ಮತ್ತೊಂದು ಎಲೆ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ',
      emptyUploadPrompt: 'ದಯವಿಟ್ಟು ಮೊದಲು ಎಲೆಯ ಫೋಟೋ ಆಯ್ಕೆಮಾಡಿ.',
      unsuitableTitle: 'ಈ ಚಿತ್ರವು ಬೆಳೆ ರೋಗ ಪತ್ತೆಗೆ ಸೂಕ್ತವಾಗಿಲ್ಲ',
      unsuitablePrompt:
        'ದಯವಿಟ್ಟು ಬಾಧಿತ ಬೆಳೆಯ ಎಲೆಯ ಸ್ಪಷ್ಟ ಕ್ಲೋಸ್-ಅಪ್ ಫೋಟೋವನ್ನು ಸೆರೆಹಿಡಿಯಿರಿ ಅಥವಾ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.',
      retakePhoto: 'ಮತ್ತೆ ಫೋಟೋ ತೆಗೆಯಿರಿ',
    },
    ask: {
      title: 'ಫಾರ್ಮ್‌ಸಾಥಿ ಬಳಿ ಕೇಳಿ',
      subtitle: 'ಬೆಳೆಗಳು, ಹವಾಮಾನ, ಕೀಟ ರಕ್ಷಣೆ ಅಥವಾ ಗೊಬ್ಬರಗಳ ಬಗ್ಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆ ಕೇಳಿ.',
      inputPlaceholder: 'ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...',
      speak: 'ಮಾತನಾಡಿ',
      listening: 'ಆಲಿಸಲಾಗುತ್ತಿದೆ... ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ',
      stop: 'ನಿಲ್ಲಿಸಿ',
      send: 'ಕಳುಹಿಸಿ',
      commonQuestions: 'ರೈತರು ಹೆಚ್ಚಾಗಿ ಕೇಳುವ ಪ್ರಶ್ನೆಗಳು',
      q1: 'ಇಂದು ನನ್ನ ಜಮೀನಿನಲ್ಲಿ ಮಳೆಯಾಗುವುದೇ?',
      q2: 'ಭತ್ತದ ಬೆಂಕಿರೋಗವನ್ನು ಹೇಗೆ ನಿರ್ವಹಿಸುವುದು?',
      q3: 'ಗೋಧಿಗೆ ಶಿಫಾರಸು ಮಾಡಲಾದ ಗೊಬ್ಬರದ ವೇಳಾಪಟ್ಟಿ ಯಾವುದು?',
      q4: 'ಬೆಳೆಗಳಿಗೆ ಯಾವಾಗ ನೀರು ಹರಿಸಬೇಕು?',
      consulting: 'ಫಾರ್ಮ್‌ಸಾಥಿ ಸಲಹಾ ಇಂಜಿನ್ ಸಂಪರ್ಕಿಸಲಾಗುತ್ತಿದೆ...',
      loginRequired: 'ಕೃಷಿ ಸಲಹೆ ಪಡೆಯಲು ದಯವಿಟ್ಟು ಸೈನ್ ಇನ್ ಮಾಡಿ.',
      loginToAsk: 'ಕೇಳಲು ಸೈನ್ ಇನ್ ಮಾಡಿ',
      submitQuestion: 'ಫಾರ್ಮ್‌ಸಾಥಿ ಬಳಿ ಕೇಳಿ',
      submitWithPhoto: 'ಪ್ರಶ್ನೆ ಮತ್ತು ಫೋಟೋ ಕಳುಹಿಸಿ',
      retry: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ',
      errorTitle: 'ಸಲಹಾ ಸೂಚನೆ',
    },
    myCrops: {
      title: 'ನನ್ನ ಬೆಳೆಗಳು',
      subtitle: 'ನಿಮ್ಮ ಬೆಳೆಗಳು, ಮಣ್ಣಿನ ಶಿಫಾರಸುಗಳು ಮತ್ತು ಬೆಳವಣಿಗೆಯ ಹಂತಗಳನ್ನು ಗಮನಿಸಿ.',
      addCrop: 'ಬೆಳೆ ಸೇರಿಸಿ',
      cropName: 'ಬೆಳೆಯ ಹೆಸರು',
      cropNamePlaceholder: 'ಬೆಳೆಯ ಹೆಸರು (ಉದಾ: ಭತ್ತ, ಹತ್ತಿ)',
      emptyTitle: 'ಇನ್ನೂ ಯಾವುದೇ ಬೆಳೆಗಳನ್ನು ಸೇರಿಸಲಾಗಿಲ್ಲ.',
      emptySubtitle:
        'ನಿಮ್ಮ ಬೆಳೆಗಳನ್ನು ದಾಖಲಿಸಿ ಅವುಗಳ ಬೆಳವಣಿಗೆಯನ್ನು ಇಲ್ಲಿ ಗಮನಿಸಿ.',
      findCropButton: 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆ ಹುಡುಕಿ',
      activeCrops: 'ಸಕ್ರಿಯ ಬೆಳೆಗಳು',
      plantedOn: 'ಬಿತ್ತನೆಯ ದಿನಾಂಕ',
      recommendedConditions: 'ಶಿಫಾರಸು ಮಾಡಿದ ಪರಿಸ್ಥಿತಿಗಳು',
    },
    history: {
      title: 'ಕೃಷಿ ಇತಿಹಾಸ',
      subtitle: 'ಹಿಂದಿನ ಬೆಳೆ ಶಿಫಾರಸುಗಳು, ರೋಗ ಪತ್ತೆ ಮತ್ತು ಕೃಷಿ ಸಲಹೆಗಳನ್ನು ವೀಕ್ಷಿಸಿ.',
      tabAll: 'ಎಲ್ಲಾ ಚಟುವಟಿಕೆಗಳು',
      tabCrops: 'ಬೆಳೆ ಶಿಫಾರಸುಗಳು',
      tabDiagnosis: 'ರೋಗ ಪತ್ತೆ',
      tabAdvisory: 'ಕೃಷಿ ಸಲಹೆಗಳು',
      emptyTitle: 'ಯಾವುದೇ ಚಟುವಟಿಕೆಗಳಿಲ್ಲ.',
      emptySubtitle: 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳು ಮತ್ತು ರೋಗ ಪತ್ತೆ ಇಲ್ಲಿ ದಾಖಲಾಗುತ್ತವೆ.',
    },
    common: {
      loading: 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
      save: 'ಉಳಿಸಿ',
      cancel: 'ರದ್ದುಮಾಡಿ',
      close: 'ಮುಚ್ಚಿ',
      error: 'ದೋಷ ಸಂಭವಿಸಿದೆ',
      tryAgain: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ',
      guestMode: 'ಅತಿಥಿ ಮೋಡ್',
      saved: 'ಇತಿಹಾಸದಲ್ಲಿ ಉಳಿಸಲಾಗಿದೆ',
      searchLocation: 'ನಗರ ಅಥವಾ ಹಳ್ಳಿ ಹುಡುಕಿ',
      useCurrentLocation: 'GPS ಸ್ಥಳ ಬಳಸಿ',
      enterCityName: 'ನಗರ ಅಥವಾ ಜಿಲ್ಲೆಯ ಹೆಸರು ಬರೆಯಿರಿ...',
      search: 'ಹುಡುಕಿ',
      locationNotFound: 'ಸ್ಥಳ ಕಂಡುಬಂದಿಲ್ಲ. ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.',
      voice_input: 'ಧ್ವನಿ ಇನ್‌ಪುಟ್',
      speak_placeholder: 'ಪ್ರಶ್ನೆ ಮಾತನಾಡಿ',
      camera_upload: 'ಚಿತ್ರ ಸೇರಿಸಿ',
      disease_detection: 'ರೋಗ ಪತ್ತೆ',
      crop_recommendation: 'ಬೆಳೆ ಶಿಫಾರಸು',
      advisory: 'ಕೃಷಿ ಸಲಹೆ',
      recent_activity: 'ಇತ್ತೀಚಿನ ಚಟುವಟಿಕೆಗಳು',
      no_activity: 'ಯಾವುದೇ ಚಟುವಟಿಕೆಗಳಿಲ್ಲ',
      no_activity_desc: 'ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳು ಮತ್ತು ರೋಗ ಪತ್ತೆ ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ.',
      ask_new_question: 'ಹೊಸ ಪ್ರಶ್ನೆ',
      ask_question: 'ಪ್ರಶ್ನೆ ಕೇಳಿ',
      queries: 'ಪ್ರಶ್ನೆಗಳು',
      type_placeholder: 'ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಬರೆಯಿರಿ...',
      foliage_context: 'ಎಲೆಯ ಮಾಹಿತಿ',
      crop_health: 'ಬೆಳೆ ಆರೋಗ್ಯ',
      all: 'ಎಲ್ಲಾ ಚಟುವಟಿಕೆಗಳು',
      back: 'ಹಿಂದೆ',
      listening: 'ಆಲಿಸಲಾಗುತ್ತಿದೆ...',
      reverse_geocoding_failed: 'ಸ್ಥಳದ ಹೆಸರನ್ನು ಗುರುತಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಹಸ್ತಚಾಲಿತವಾಗಿ ಆಯ್ಕೆಮಾಡಿ.',
    },
  },

  mr: {
    nav: {
      brand: 'फार्मसाथी',
      home: 'मुख्यपृष्ठ',
      ask: 'विचारा',
      myCrops: 'माझी पिके',
      diagnosis: 'रोग निदान',
      cropRecommendation: 'पीक शिफारस',
      history: 'इतिहास',
      profile: 'प्रोफाइल',
      login: 'लॉगिन',
      logout: 'लॉगआउट',
      selectLocation: 'स्थान निवडा',
      detectLocation: 'GPS स्थान शोधा',
    },
    welcome: {
      title: 'फार्मसाथीमध्ये आपले स्वागत आहे',
      tagline: 'तुमचा डिजिटल शेती साथीदार',
      description:
        'फार्मसाथी भारतीय शेतकऱ्यांना अचूक पीक शिफारसी, रोग निदान, हवामान अंदाज आणि तज्ज्ञ कृषी सल्ला प्रदान करते.',
      selectLanguagePrompt: 'आपली भाषा निवडा',
      continueButton: 'पुढे जा',
      cropRec: 'स्मार्ट पीक शिफारस',
      cropRecDesc: 'मातीचे पोषण आणि हवामानानुसार सर्वोत्तम पीक निवडा.',
      disease: 'त्वरित पान रोग निदान',
      diseaseDesc: 'पानांचे फोटो स्कॅन करून रोग ओळखा आणि सेंद्रिय व्यवस्थापन उपाय मिळवा.',
      weather: 'अचूक कृषी हवामान',
      weatherDesc: 'थेट पावसाचा अंदाज, तापमान आणि स्थानिक शेती सल्ला.',
    },
    permissions: {
      title: 'फार्मसाथी सेटअप',
      subtitle: 'फार्मसाथीच्या उत्तम सेवेसाठी परवानग्या निवडा.',
      optionalBadge: 'पर्यायी',
      locationTitle: 'स्थान (लोकेशन)',
      locationDesc: 'स्थानिक हवामान, पाऊस आणि शेती सल्ल्यासाठी.',
      locationDetecting: 'स्थान शोधत आहे...',
      locationEnabled: 'स्थान आढळले',
      locationAllow: 'सध्याचे स्थान वापरा',
      locationManualOption: 'स्थान स्वतः निवडा',
      locationUnavailable: 'स्थान उपलब्ध नाही. तुम्ही जिल्हा स्वतः निवडू शकता.',
      locationContext: 'स्थानिक हवामान आणि संदर्भ',
      cameraTitle: 'कॅमेरा',
      cameraDesc: 'रोगाच्या निदानासाठी पिकाच्या पानांचा फोटो काढा.',
      cameraReady: 'कॅमेरा तयार आहे',
      cameraContext: 'रोग निदान फोटो',
      cameraEnabled: 'कॅमेरा चालू आहे',
      cameraAllow: 'कॅमेरा परवानगी द्या',
      cameraFallback: 'गॅलरीमधून फोटो अपलोड करू शकता',
      micTitle: 'मायक्रोफोन',
      micDesc: 'शेतीचे प्रश्न आपल्या भाषेत बोलून विचारा.',
      micReady: 'माइक तयार आहे',
      micContext: 'आपल्या भाषेत आवाज प्रश्न',
      micEnabled: 'माइक चालू आहे',
      micAllow: 'माइक परवानगी द्या',
      micFallback: 'टाइप करूनही प्रश्न विचारू शकता',
      optionalNotice:
        'परवानग्या पर्यायी आहेत. परवानगी नाकारली तरी तुम्ही मॅन्युअली स्थान आणि फोटो निवडू शकता.',
      skipForNow: 'आता वगळा',
      continue: 'पुढे जा',
    },
    dashboard: {
      greeting: 'नमस्कार, शेतकरी मित्र',
      heroTitle: 'तुमचा स्मार्ट शेती मार्गदर्शक',
      heroSubtitle:
        'आजचे हवामान, पिकांचे आरोग्य, सर्वोत्तम पीक किंवा कोणताही शेतीविषयक प्रश्न विचारा.',
      askPlaceholder: 'तुमचे पीक, पाऊस, खत किंवा मातीबद्दल काहीही विचारा...',
      askButton: 'विचारा',
      quickActions: 'महत्त्वाच्या शेती सेवा',
      actionCropRec: 'सर्वोत्तम पीक शोधा',
      actionCropRecDesc: 'माती परीक्षणानुसार AI पीक शिफारस',
      actionDiagnosis: 'पीक रोग निदान',
      actionDiagnosisDesc: 'पानांचे फोटो स्कॅन करून उपाय मिळवा',
      actionAsk: 'शेती सल्लागारास विचारा',
      actionAskDesc: 'शेतीविषयक प्रश्नांवर त्वरित मार्गदर्शन',
      actionMyCrops: 'माझी पिके',
      actionMyCropsDesc: 'पिकांची वाढ आणि काळजी नोंदवा',
      recentActivity: 'अलीकडील शेती नोंदी',
      noActivity: 'कोणतीही अलीकडील नोंद नाही.',
      noActivityDesc:
        'प्रश्न विचारल्यावर किंवा पीक शिफारस केल्यावर तुमचा इतिहास येथे दिसेल.',
      viewAll: 'सर्व इतिहास पहा',
    },
    weather: {
      cardTitle: 'आजचे शेतातील हवामान',
      temperature: 'तापमान',
      humidity: 'आर्द्रता',
      rainfall: 'पाऊस',
      wind: 'वाऱ्याचा वेग',
      forecast: '७ दिवसांचा हवामान अंदाज',
      loading: 'हवामान माहिती आणत आहे...',
      unavailable: 'हवामान माहिती उपलब्ध नाही.',
      selectLocationPrompt: 'थेट हवामान पाहण्यासाठी कृपया आपले स्थान निवडा.',
    },
    cropRec: {
      title: 'आपल्या शेतासाठी सर्वोत्तम पीक निवडा',
      subtitle:
        'मातीचे घटक (N-P-K) आणि हवामान नोंदी भरून सर्वोत्तम पीक जाणून घ्या.',
      soilNutrients: 'मातीतील पोषक घटक (N - P - K)',
      nitrogen: 'नायट्रोजन (N) - किलो/हेक्टर',
      nitrogenPlaceholder: 'नायट्रोजन मूल्य (उदा. २० - १४०)',
      phosphorus: 'फॉस्फरस (P) - किलो/हेक्टर',
      phosphorusPlaceholder: 'फॉस्फरस मूल्य (उदा. १० - १००)',
      potassium: 'पोटॅश (K) - किलो/हेक्टर',
      potassiumPlaceholder: 'पोटॅश मूल्य (उदा. १० - १००)',
      climateConditions: 'हवामान आणि जमिनीची स्थिती',
      temperature: 'तापमान (°C)',
      temperaturePlaceholder: 'तापमान नोंदवा (१५ - ४०)',
      humidity: 'आर्द्रता (%)',
      humidityPlaceholder: 'आर्द्रता नोंदवा (३० - ९०)',
      ph: 'जमिनीचा pH (० - १४)',
      phPlaceholder: 'pH मूल्य (उदा. ५.५ - ७.५)',
      rainfall: 'वार्षिक पाऊस (मिमी)',
      rainfallPlaceholder: 'पाऊस नोंदवा (उदा. १०० - ३००)',
      fillFromWeather: 'सध्याच्या हवामानातून तापमान व आर्द्रता भरा',
      calculateButton: 'शिफारस केलेले पीक मोजा',
      calculating: 'माती व हवामानाचे विश्लेषण सुरू आहे...',
      resultTitle: 'शिफारस केलेले पीक',
      whyThisCrop: 'हे पीक का निवडावे?',
      whyDesc:
        'मातीतील पोषण, pH आणि हवामानाच्या आधारे हे पीक सर्वोत्तम उत्पादन देईल.',
      inputSummary: 'नोंदवलेली माहिती',
      checkAnother: 'दुसऱ्या शेताची तपासणी करा',
    },
    disease: {
      title: 'पीक पान रोग निदान',
      subtitle:
        'त्वरित रोग ओळख आणि जैविक उपायांसाठी बाधित पानाचा फोटो काढा किंवा अपलोड करा.',
      takePhoto: 'कॅमेऱ्याने फोटो काढा',
      uploadPhoto: 'गॅलरीतून अपलोड करा',
      changePhoto: 'फोटो बदला',
      diagnoseButton: 'आरोग्य तपासा',
      diagnosing: 'पानाची तपासणी सुरू आहे...',
      resultTitle: 'रोग निदान निकाल',
      cropDetected: 'पीक',
      conditionDetected: 'आढळलेला रोग / स्थिती',
      confidenceLabel: 'अचूकता',
      healthyFoliage: 'निरोगी पाने',
      diseaseDetected: 'रोगाची लक्षणे आढळली',
      managementGuidance: 'व्यवस्थापन आणि शेती उपाय',
      culturalPractices: 'कृषी पद्धती',
      sanitation: 'शेताची स्वच्छता',
      prevention: 'प्रतिबंधात्मक उपाय',
      disclaimer:
        'रासायनिक फवारणीसाठी जवळच्या कृषी विज्ञान केंद्राशी (KVK) संपर्क साधा.',
      scanAnother: 'दुसरे पान स्कॅन करा',
      emptyUploadPrompt: 'कृपया आधी पानाचा फोटो निवडा.',
      unsuitableTitle: 'ही प्रतिमा पीक रोग निदानासाठी योग्य नाही',
      unsuitablePrompt:
        'कृपया बाधीत पिकाच्या पानाचा स्पष्ट क्लोज-अप फोटो काढा किंवा अपलोड करा.',
      retakePhoto: 'पुन्हा फोटो काढा',
    },
    ask: {
      title: 'फार्मसाथीला विचारा',
      subtitle: 'पिके, हवामान, कीटक नियंत्रण किंवा खतांबद्दल कोणताही प्रश्न विचारा.',
      inputPlaceholder: 'तुमचा शेतीविषयक प्रश्न येथे लिहा...',
      speak: 'बोला',
      listening: 'ऐकत आहे... स्पष्ट बोला',
      stop: 'थांबवा',
      send: 'पाठवा',
      commonQuestions: 'वारंवार विचारले जाणारे प्रश्न',
      q1: 'आज माझ्या शेतात पाऊस पडेल का?',
      q2: 'भातावरील करपा रोगाचे नियंत्रण कसे करावे?',
      q3: 'गव्हासाठी खतांचे योग्य वेळापत्रक काय आहे?',
      q4: 'पिकांना पाणी कधी द्यावे?',
      consulting: 'फार्मसाथी सल्ला इंजिनशी सल्लामसलत सुरू आहे...',
      loginRequired: 'शेती सल्ला मिळवण्यासाठी कृपया लॉगिन करा.',
      loginToAsk: 'विचारण्यासाठी लॉगिन करा',
      submitQuestion: 'फार्मसाथीला विचारा',
      submitWithPhoto: 'प्रश्न आणि फोटो पाठवा',
      retry: 'पुन्हा प्रयत्न करा',
      errorTitle: 'सल्ला सूचना',
    },
    myCrops: {
      title: 'माझी पिके',
      subtitle: 'तुमची पिके, मातीची शिफारस आणि वाढीच्या टप्प्यांवर लक्ष ठेवा.',
      addCrop: 'पीक जोडा',
      cropName: 'पिकाचे नाव',
      cropNamePlaceholder: 'पिकाचे नाव (उदा. कापूस, सोयाबीन)',
      emptyTitle: 'अद्याप कोणतेही पीक जोडलेले नाही.',
      emptySubtitle:
        'पिकांची नोंद ठेवून त्यांची वाढ आणि काळजी येथे ट्रॅक करा.',
      findCropButton: 'शिफारस केलेले पीक शोधा',
      activeCrops: 'सक्रिय पिके',
      plantedOn: 'लागवड तारीख',
      recommendedConditions: 'शिफारस केलेल्या परिस्थिती',
    },
    history: {
      title: 'कृषी इतिहास',
      subtitle: 'तुमच्या मागील पीक शिफारसी, रोग तपासणी आणि शेती सल्ला पहा.',
      tabAll: 'सर्व नोंदी',
      tabCrops: 'पीक शिफारसी',
      tabDiagnosis: 'रोग निदान',
      tabAdvisory: 'शेती सल्ला',
      emptyTitle: 'कोणताही इतिहास उपलब्ध नाही.',
      emptySubtitle: 'तुमचे प्रश्न आणि रोग तपासणी येथे जतन केली जाईल.',
    },
    common: {
      loading: 'लोड होत आहे...',
      save: 'जतन करा',
      cancel: 'रद्द करा',
      close: 'बंद करा',
      error: 'त्रुटी आढळली',
      tryAgain: 'पुन्हा प्रयत्न करा',
      guestMode: 'अतिथी मोड',
      saved: 'इतिहासात जतन केले',
      searchLocation: 'शहर किंवा गाव शोधा',
      useCurrentLocation: 'GPS स्थान वापरा',
      enterCityName: 'शहर किंवा जिल्ह्याचे नाव लिहा...',
      search: 'शोधा',
      locationNotFound: 'स्थान आढळले नाही. पुन्हा प्रयत्न करा.',
      voice_input: 'व्हॉइस इनपुट',
      speak_placeholder: 'प्रश्न बोला',
      camera_upload: 'फोटो जोडा',
      disease_detection: 'रोग निदान',
      crop_recommendation: 'पीक शिफारस',
      advisory: 'शेती सल्ला',
      recent_activity: 'अलीकडील नोंदी',
      no_activity: 'नोंदी उपलब्ध नाहीत',
      no_activity_desc: 'तुमचे प्रश्न आणि रोग तपासणी येथे दिसतील.',
      ask_new_question: 'नवीन सत्र',
      ask_question: 'प्रश्न विचारा',
      queries: 'प्रश्न',
      type_placeholder: 'तुमचा शेतीविषयक प्रश्न येथे लिहा...',
      foliage_context: 'पानांची स्थिती',
      crop_health: 'पीक आरोग्य',
      all: 'सर्व नोंदी',
      back: 'मागे',
      listening: 'ऐकत आहे...',
      reverse_geocoding_failed: 'गावाचे नाव ओळखता आले नाही. कृपया स्वतः निवडा.',
    },
  },
};
