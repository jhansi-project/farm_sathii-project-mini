import React, { useState, useRef, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useLanguageStore, SUPPORTED_LANGUAGES } from '../../stores/languageStore';
import { useLocationStore } from '../../stores/locationStore';
import { useTranslation } from '../../i18n/useTranslation';
import { LocationModal } from './LocationModal';
import { AppNavTab } from '../../features/dashboard/DashboardView';

export { SUPPORTED_LANGUAGES };

interface NavbarProps {
  onOpenAuth: () => void;
  onOpenProfile: () => void;
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
  activeTab?: AppNavTab;
  onChangeTab?: (tab: AppNavTab) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenAuth,
  onOpenProfile,
  activeTab = 'home',
  onChangeTab,
}) => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const { currentLanguage, setLanguage } = useLanguageStore();
  const { locationName } = useLocationStore();
  const { t } = useTranslation();

  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);

  const langMenuRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (langMenuRef.current && !langMenuRef.current.contains(event.target as Node)) {
        setShowLangMenu(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const activeLangObj =
    SUPPORTED_LANGUAGES.find((l) => l.code === currentLanguage) || SUPPORTED_LANGUAGES[0];

  const displayLocation = locationName || t.nav.selectLocation;

  const desktopNavItems: Array<{ id: AppNavTab; label: string; icon: string }> = [
    { id: 'home', label: t.nav.home, icon: 'home' },
    { id: 'ask', label: t.nav.ask, icon: 'forum' },
    { id: 'crops', label: t.nav.cropRecommendation, icon: 'psychology' },
    { id: 'diagnosis', label: t.nav.diagnosis, icon: 'photo_camera' },
    { id: 'my-crops', label: t.nav.myCrops, icon: 'agriculture' },
    { id: 'history', label: t.nav.history, icon: 'history' },
  ];

  return (
    <>
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 50,
          backgroundColor: 'var(--color-header-bg, #2f3e20)',
          borderBottom: '1px solid var(--color-header-border, #2f3e20)',
          boxShadow: 'var(--shadow-xs)',
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 1.25rem',
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '1240px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.5rem',
          }}
        >
          {/* Left: Brand Identity */}
          <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
            <div
              onClick={() => onChangeTab?.('home')}
              style={{
                display: 'flex',
                alignItems: 'center',
                cursor: 'pointer',
                userSelect: 'none',
              }}
            >
              <img
                src="/assets/farmsathi_logo.png"
                alt="FarmSathi"
                style={{
                  height: '40px',
                  width: 'auto',
                  maxHeight: 'calc(var(--header-height, 64px) - 16px)',
                  objectFit: 'contain',
                  display: 'block',
                }}
              />
            </div>
          </div>

          {/* Center: Desktop Navigation Bar (Visible on >= 900px screens) */}
          {onChangeTab && (
            <nav
              style={{
                display: 'none',
                alignItems: 'center',
                gap: '0.25rem',
              }}
              className="navbar-desktop-nav"
            >
              <style>{`
                @media (min-width: 900px) {
                  .navbar-desktop-nav {
                    display: flex !important;
                  }
                }
              `}</style>
              {desktopNavItems.map((item) => {
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => onChangeTab(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                      padding: '0.45rem 0.65rem',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: isActive ? 'var(--color-active, #889063)' : 'transparent',
                      color: isActive ? 'var(--color-text-inverse, #E5D7C4)' : 'var(--color-header-text, #E5D7C4)',
                      fontWeight: isActive ? 700 : 500,
                      fontSize: 'var(--font-size-sm)',
                      transition: 'all var(--transition-fast)',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(136, 144, 99, 0.25)';
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <span
                      className="material-symbols-outlined"
                      style={{
                        fontSize: '18px',
                        color: 'inherit',
                        fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0",
                      }}
                    >
                      {item.icon}
                    </span>
                    <span
                      style={
                        item.id === 'crops' || item.id === 'my-crops'
                          ? { whiteSpace: 'nowrap' }
                          : undefined
                      }
                    >
                      {item.label}
                    </span>
                  </button>
                );
              })}
            </nav>
          )}

          {/* Right: Location, Language, and Profile / Login */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexShrink: 0 }}>
            {/* Location Chip */}
            <button
              type="button"
              onClick={() => setIsLocationModalOpen(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                backgroundColor: 'var(--color-surface, #E5D7C4)',
                color: 'var(--color-icon-primary, #354024)',
                borderRadius: 'var(--radius-full)',
                padding: '0.4rem 0.75rem',
                border: '1px solid var(--color-border, #CFBB99)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
              }}
              title="Click to detect or change location"
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-surface-hover, #CFBB99)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--color-surface, #E5D7C4)';
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                location_on
              </span>
              <span
                style={{
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 600,
                  maxWidth: '130px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {displayLocation}
              </span>
              <span className="material-symbols-outlined" style={{ fontSize: '16px', opacity: 0.7 }}>
                expand_more
              </span>
            </button>

            {/* Language Selector Dropdown */}
            <div style={{ position: 'relative' }} ref={langMenuRef}>
              <button
                type="button"
                onClick={() => {
                  setShowLangMenu(!showLangMenu);
                  setShowUserMenu(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  padding: '0.4rem 0.75rem',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--color-border, #CFBB99)',
                  backgroundColor: 'var(--color-surface, #E5D7C4)',
                  color: 'var(--color-icon-primary, #354024)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-hover, #CFBB99)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface, #E5D7C4)';
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                  translate
                </span>
                <span>{activeLangObj.name}</span>
                <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                  expand_more
                </span>
              </button>

              {showLangMenu && (
                <div
                  style={{
                    position: 'absolute',
                    right: 0,
                    top: '115%',
                    backgroundColor: 'var(--color-surface, #E5D7C4)',
                    borderRadius: 'var(--radius-lg)',
                    boxShadow: 'var(--shadow-lg)',
                    border: '1px solid var(--color-border, #CFBB99)',
                    minWidth: '170px',
                    zIndex: 100,
                    overflow: 'hidden',
                    padding: '0.25rem 0',
                  }}
                >
                  {SUPPORTED_LANGUAGES.map((l) => (
                    <button
                      key={l.code}
                      type="button"
                      onClick={() => {
                        setLanguage(l.code);
                        setShowLangMenu(false);
                      }}
                      style={{
                        width: '100%',
                        padding: '0.65rem 1rem',
                        textAlign: 'left',
                        fontSize: 'var(--font-size-xs)',
                        fontWeight: currentLanguage === l.code ? 700 : 500,
                        color:
                          currentLanguage === l.code
                            ? 'var(--color-primary, #4C3D19)'
                            : 'var(--color-on-surface, #4C3D19)',
                        backgroundColor:
                          currentLanguage === l.code ? 'var(--color-surface-container, #CFBB99)' : 'transparent',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        cursor: 'pointer',
                        transition: 'background-color var(--transition-fast)',
                      }}
                      onMouseEnter={(e) => {
                        if (currentLanguage !== l.code) {
                          e.currentTarget.style.backgroundColor = 'var(--color-surface-hover, #CFBB99)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (currentLanguage !== l.code) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      <span>{l.nativeName}</span>
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted, #889063)' }}>
                        {l.name}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Profile / Auth Menu */}
            {isAuthenticated ? (
              <div style={{ position: 'relative' }} ref={userMenuRef}>
                <button
                  type="button"
                  onClick={() => {
                    setShowUserMenu(!showUserMenu);
                    setShowLangMenu(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    padding: '0.35rem 0.75rem',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: 'var(--color-surface, #E5D7C4)',
                    color: 'var(--color-primary, #4C3D19)',
                    cursor: 'pointer',
                    border: '1px solid var(--color-border, #CFBB99)',
                  }}
                >
                  <span
                    className="material-symbols-outlined"
                    style={{ fontSize: '20px', color: 'var(--color-icon-primary, #354024)' }}
                  >
                    account_circle
                  </span>
                  <span
                    style={{
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 700,
                      maxWidth: '100px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {user?.full_name || 'Farmer'}
                  </span>
                </button>

                {showUserMenu && (
                  <div
                    style={{
                      position: 'absolute',
                      right: 0,
                      top: '115%',
                      backgroundColor: 'var(--color-surface, #E5D7C4)',
                      borderRadius: 'var(--radius-lg)',
                      boxShadow: 'var(--shadow-lg)',
                      border: '1px solid var(--color-border, #CFBB99)',
                      minWidth: '180px',
                      zIndex: 100,
                      overflow: 'hidden',
                      padding: '0.35rem 0',
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => {
                        setShowUserMenu(false);
                        onOpenProfile();
                      }}
                      style={{
                        width: '100%',
                        padding: '0.65rem 1rem',
                        textAlign: 'left',
                        fontSize: 'var(--font-size-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: 'var(--color-on-surface, #4C3D19)',
                        cursor: 'pointer',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--color-surface-hover, #CFBB99)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                        person
                      </span>
                      <span>{t.nav.profile}</span>
                    </button>
                    <div style={{ height: '1px', backgroundColor: 'var(--color-border, #CFBB99)' }} />
                    <button
                      type="button"
                      onClick={() => {
                        setShowUserMenu(false);
                        logout();
                      }}
                      style={{
                        width: '100%',
                        padding: '0.65rem 1rem',
                        textAlign: 'left',
                        fontSize: 'var(--font-size-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: 'var(--color-error, #4C3D19)',
                        cursor: 'pointer',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--color-surface-hover, #CFBB99)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                        logout
                      </span>
                      <span>{t.nav.logout}</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                type="button"
                onClick={onOpenAuth}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  padding: '0.45rem 1rem',
                  backgroundColor: 'var(--color-primary, #4C3D19)',
                  color: 'var(--color-text-inverse, #E5D7C4)',
                  borderRadius: 'var(--radius-full)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 700,
                  boxShadow: 'var(--shadow-xs)',
                  cursor: 'pointer',
                  border: '1px solid var(--color-border, #CFBB99)',
                  transition: 'background-color var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-primary-hover, #354024)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-primary, #4C3D19)';
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                  login
                </span>
                <span>{t.nav.login}</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Global Location Modal */}
      <LocationModal
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
      />
    </>
  );
};
