import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { AppNavTab, DashboardView } from '../features/dashboard/DashboardView';
import { WelcomeView } from '../features/welcome/WelcomeView';
import { PermissionSetupView } from '../features/permissions/PermissionSetupView';
import { CropRecommendationView } from '../features/crop-recommendation/CropRecommendationView';
import { DiseaseDetectionView } from '../features/disease-detection/DiseaseDetectionView';
import { AdvisoryView } from '../features/advisory/AdvisoryView';
import { HistoryView } from '../features/history/HistoryView';
import { MyCropsView } from '../features/my-crops/MyCropsView';
import { AuthModal } from '../features/auth/AuthModal';
import { ProfileModal } from '../features/profile/ProfileModal';
import { useLanguageStore } from '../stores/languageStore';

export const App: React.FC = () => {
  const { currentLanguage, hasCompletedWelcome } = useLanguageStore();

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = currentLanguage;
      document.documentElement.setAttribute('data-lang', currentLanguage);
    }
  }, [currentLanguage]);

  const [step, setStep] = useState<'welcome' | 'permissions' | 'app'>(
    hasCompletedWelcome ? 'app' : 'welcome'
  );
  const [activeTab, setActiveTab] = useState<AppNavTab>('home');
  const [advisoryQuery, setAdvisoryQuery] = useState('');
  const [advisoryConversationId, setAdvisoryConversationId] = useState<string | undefined>();
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const handleNavigate = (tab: AppNavTab, queryContext?: string, conversationId?: string) => {
    if (queryContext !== undefined) {
      setAdvisoryQuery(queryContext);
    }
    if (conversationId !== undefined) {
      setAdvisoryConversationId(conversationId);
    }
    setActiveTab(tab);
  };

  // 1. Initial Onboarding: Welcome & Language Selection
  if (step === 'welcome' && !hasCompletedWelcome) {
    return (
      <WelcomeView
        onContinue={() => {
          setStep('permissions');
        }}
      />
    );
  }

  // 2. Initial Onboarding: Dedicated Permission Setup
  if (step === 'permissions') {
    return (
      <PermissionSetupView
        onContinue={() => {
          setStep('app');
        }}
        onBack={() => {
          setStep('welcome');
        }}
      />
    );
  }

  // 3. Primary Application Hub
  const renderTabContent = () => {
    switch (activeTab) {
      case 'ask':
        return (
          <AdvisoryView
            initialQuery={advisoryQuery}
            initialConversationId={advisoryConversationId}
            onNavigateToDiagnosis={() => setActiveTab('diagnosis')}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        );
      case 'crops':
        return <CropRecommendationView />;
      case 'my-crops':
        return <MyCropsView />;
      case 'diagnosis':
        return <DiseaseDetectionView />;
      case 'history':
        return (
          <HistoryView
            onNavigate={(tab, query, convId) => handleNavigate(tab, query, convId)}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        );
      case 'profile':
      case 'home':
      default:
        return (
          <DashboardView
            onNavigate={(tab, query, convId) => handleNavigate(tab, query, convId)}
            onOpenAuth={() => setIsAuthOpen(true)}
            onOpenProfile={() => setIsProfileOpen(true)}
          />
        );
    }
  };

  return (
    <>
      <DashboardLayout
        activeTab={activeTab}
        onChangeTab={(tab) => {
          if (tab === 'profile') {
            setIsProfileOpen(true);
          } else {
            setActiveTab(tab);
          }
        }}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenProfile={() => setIsProfileOpen(true)}
      >
        {renderTabContent()}
      </DashboardLayout>

      {/* Global Modals */}
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
      <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
    </>
  );
};

export default App;
