import React from 'react';
import { AppNavTab } from '../../features/dashboard/DashboardView';
import { useTranslation } from '../../i18n/useTranslation';

interface BottomNavProps {
  activeTab: AppNavTab;
  onChangeTab: (tab: AppNavTab) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab, onChangeTab }) => {
  const { t } = useTranslation();

  const tabs = [
    { id: 'home' as AppNavTab, label: t.nav.home, icon: 'home' },
    { id: 'ask' as AppNavTab, label: t.nav.ask, icon: 'forum' },
    { id: 'crops' as AppNavTab, label: t.nav.cropRecommendation, icon: 'psychology' },
    { id: 'diagnosis' as AppNavTab, label: t.nav.diagnosis, icon: 'photo_camera' },
    { id: 'my-crops' as AppNavTab, label: t.nav.myCrops, icon: 'agriculture' },
    { id: 'history' as AppNavTab, label: t.nav.history, icon: 'history' },
  ];

  return (
    <nav
      className="mobile-bottom-nav"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: 'var(--color-header-bg, #2f3e20)',
        borderTop: '1px solid var(--color-header-border, #2f3e20)',
        boxShadow: '0 -2px 10px rgba(53, 64, 36, 0.12)',
        zIndex: 35,
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        padding: '0.4rem 0.25rem calc(0.4rem + env(safe-area-inset-bottom, 0px)) 0.25rem',
        boxSizing: 'border-box',
      }}
      aria-label="Bottom Navigation"
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChangeTab(tab.id)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0.35rem 0.5rem',
              borderRadius: 'var(--radius-md)',
              backgroundColor: isActive ? 'var(--color-active, #889063)' : 'transparent',
              color: isActive ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-header-text, #E5D7C4)',
              minWidth: '50px',
              minHeight: '44px',
              transition: 'all var(--transition-fast)',
              cursor: 'pointer',
              border: 'none',
            }}
          >
            <span
              className="material-symbols-outlined"
              style={{
                fontSize: '22px',
                fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0",
              }}
            >
              {tab.icon}
            </span>
            <span
              style={{
                fontSize: '11px',
                fontWeight: isActive ? 700 : 500,
                marginTop: '0.15rem',
                whiteSpace: 'nowrap',
                maxWidth: '60px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {tab.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
};

