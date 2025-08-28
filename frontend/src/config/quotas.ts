// Configuration des quotas et délais pour éviter les erreurs de rate limiting

export const QUOTA_CONFIG = {
  // Délais entre les clients (en millisecondes)
  DELAY_BETWEEN_CLIENTS: 2000, // 2 secondes
  
  // Configuration des retries
  MAX_RETRIES: 3,
  
  // Délais de backoff pour les erreurs de quota (en millisecondes)
  QUOTA_RETRY_DELAYS: [
    30 * 1000,  // 30 secondes pour le premier retry
    60 * 1000,  // 60 secondes pour le deuxième retry
    90 * 1000   // 90 secondes pour le troisième retry
  ],
  
  // Délais de backoff pour les autres erreurs (en millisecondes)
  GENERAL_RETRY_DELAYS: [
    2000,   // 2 secondes
    4000,   // 4 secondes
    8000    // 8 secondes
  ],
  
  // Limites de quotas Google Sheets
  GOOGLE_SHEETS: {
    REQUESTS_PER_MINUTE: 60,
    REQUESTS_PER_SECOND: 1,
    SAFETY_MARGIN: 0.8 // Utiliser seulement 80% du quota pour être sûr
  },
  
  // Messages d'erreur pour détecter les problèmes de quota
  QUOTA_ERROR_PATTERNS: [
    '429',
    'quota',
    'rate limit',
    'Quota exceeded',
    'ReadRequestsPerMinutePerUser',
    'sheets.googleapis.com'
  ]
};

// Fonction utilitaire pour calculer le délai de retry
export const getRetryDelay = (retryIndex: number, isQuotaError: boolean): number => {
  if (isQuotaError) {
    return QUOTA_CONFIG.QUOTA_RETRY_DELAYS[retryIndex] || QUOTA_CONFIG.QUOTA_RETRY_DELAYS[QUOTA_CONFIG.QUOTA_RETRY_DELAYS.length - 1];
  } else {
    return QUOTA_CONFIG.GENERAL_RETRY_DELAYS[retryIndex] || QUOTA_CONFIG.GENERAL_RETRY_DELAYS[QUOTA_CONFIG.GENERAL_RETRY_DELAYS.length - 1];
  }
};

// Fonction pour détecter les erreurs de quota
export const isQuotaError = (errorMessage: string): boolean => {
  const lowerMessage = errorMessage.toLowerCase();
  return QUOTA_CONFIG.QUOTA_ERROR_PATTERNS.some(pattern => 
    lowerMessage.includes(pattern.toLowerCase())
  );
};
