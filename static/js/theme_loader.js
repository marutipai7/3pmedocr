document.addEventListener('DOMContentLoaded', function() {
    const ELEMENT_COLOR_MAPPINGS = {
        'home-bg': { className: 'home-bg', styleProperty: 'backgroundColor' },
        'maps-bg': { className: 'map-bg', styleProperty: 'backgroundColor' },
        'points-bg': { className: 'points-bg', styleProperty: 'backgroundColor' },
        'primary-bg': { className: 'primary-bg', styleProperty: 'backgroundColor' }
    };

    async function loadAndApplyUserTheme() {
        try {
            const response = await fetch('/settings/get_user_theme_api/');
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error fetching theme data:', errorData.error || `HTTP error! Status: ${response.status}`);
                return;
            }

            const themeData = await response.json();

            for (const semanticKey in themeData) {
                if (themeData.hasOwnProperty(semanticKey) && ELEMENT_COLOR_MAPPINGS[semanticKey]) {
                    const colorName = themeData[semanticKey];
                    const mapping = ELEMENT_COLOR_MAPPINGS[semanticKey];
                    
                    const targetElements = document.querySelectorAll(`.${mapping.className}`);
                    targetElements.forEach(targetElement => {
                        targetElement.classList.forEach(cls => {
                            if (cls.startsWith('bg-')) {
                                targetElement.classList.remove(cls);
                            }
                        });

                        const tailwindBgClass = `bg-${colorName.replace(/_/g, '-')}`;
                        targetElement.classList.add(tailwindBgClass);
                    });
                }
            }

        } catch (error) {
            console.error('ERROR: Network or JS error during theme application:', error);
        }
    }

    loadAndApplyUserTheme();

});

// document.addEventListener('DOMContentLoaded', function() {
//     async function loadAndApplyUserTheme() {
//         try {
//             const response = await fetch('/settings/get_user_theme_api/'); 
//             if (!response.ok) {
//                 const errorData = await response.json();
//                 console.error('Error fetching theme data:', errorData.error || `HTTP error! Status: ${response.status}`);
//                 return; 
//             }

//             const themeData = await response.json(); 
//             console.log('Fetched Theme Data (color names):', themeData);

//             const root = document.documentElement; 
            
//             for (const semanticKey in themeData) {
//                 if (themeData.hasOwnProperty(semanticKey)) {
//                     const colorName = themeData[semanticKey];
//                     const sourceCssVarName = `--color-${colorName.replace(/_/g, '-')}`; 
//                     const actualHexValue = getComputedStyle(root).getPropertyValue(sourceCssVarName).trim();
//                     const targetCssVarName = `--${semanticKey.replace(/_/g, '-')}`;

//                     if (actualHexValue) {
//                         root.style.setProperty(targetCssVarName, actualHexValue);
//                         console.log(`Applied ${targetCssVarName} -> ${actualHexValue} (from ${sourceCssVarName})`);
//                     } else {
//                         console.warn(`Could not resolve CSS variable ${sourceCssVarName} for ${semanticKey}. Using default.`);
//                     }
//                 }
//             }
//             console.log('User theme applied successfully!');

//         } catch (error) {
//             console.error('Network or JS error applying theme:', error);
//         }
//     }

//     loadAndApplyUserTheme();
// });



// document.addEventListener('DOMContentLoaded', function() {
//     async function loadAndApplyUserTheme() {
//         const themeColor = document.getElementById('theme-color');
//         if (!themeColor) {
//             console.warn('Theme color element with ID "theme-color" not found. Cannot apply dynamic theme.');
//             return;
//         }

//         try {
//             const response = await fetch('/settings-api/theme/');

//             if (!response.ok) {
//                 const errorData = await response.json();
//                 console.error('Error fetching header background class:', errorData.error || `HTTP error! Status: ${response.status}`);

//                 themeColor.classList.add('bg-gray-500'); 
//                 return;
//             }

//             const themeData = await response.json();
//             const BgClass = themeData.bg_class; 

//             themeColor.classList.add(BgClass);
//             console.log('Applied dynamic header background class:', BgClass);

//         } catch (error) {
//             console.error('Network or JS error applying header background class:', error);
//             themeColor.classList.add('bg-red-500'); // Another visual fallback for debugging
//         }
//     }

//     loadAndApplyUserTheme();
// });