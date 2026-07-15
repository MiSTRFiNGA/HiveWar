(function (global) {
  "use strict";

  const platform = "poki";
  let sdk = null;
  const noop = () => {};
  const resolved = () => Promise.resolve(false);

  async function loadScript(src) {
    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  const ready = (async () => {
    try {
      if (platform === "crazygames") {
        await loadScript("https://sdk.crazygames.com/crazygames-sdk-v3.js");
        await global.CrazyGames.SDK.init();
        sdk = global.CrazyGames.SDK;
      } else if (platform === "poki") {
        await loadScript("https://game-cdn.poki.com/scripts/v2/poki-sdk.js");
        await global.PokiSDK.init();
        sdk = global.PokiSDK;
      }
    } catch (error) {
      console.warn("[PSDK] local/no-op fallback", error);
      sdk = null;
    }
    return sdk;
  })();

  function crazyAd(kind) {
    return new Promise((resolve) => {
      if (!sdk) return resolve(false);
      try {
        sdk.ad.requestAd(kind, {
          adStarted: () => global.dispatchEvent(new CustomEvent("psdk:adstart")),
          adFinished: () => { global.dispatchEvent(new CustomEvent("psdk:adend")); resolve(true); },
          adError: () => { global.dispatchEvent(new CustomEvent("psdk:adend")); resolve(false); },
        });
      } catch (_) { resolve(false); }
    });
  }

  global.PSDK = {
    platform,
    ready,
    loaded() {
      try {
        if (platform === "crazygames") sdk && sdk.game.loadingStop();
        else if (platform === "poki") sdk && sdk.gameLoadingFinished();
      } catch (_) {}
    },
    start() {
      try {
        if (platform === "crazygames") sdk && sdk.game.gameplayStart();
        else if (platform === "poki") sdk && sdk.gameplayStart();
      } catch (_) {}
    },
    stop() {
      try {
        if (platform === "crazygames") sdk && sdk.game.gameplayStop();
        else if (platform === "poki") sdk && sdk.gameplayStop();
      } catch (_) {}
    },
    midgame() {
      if (platform === "crazygames") return crazyAd("midgame");
      if (platform === "poki" && sdk) {
        try { return sdk.commercialBreak().then(() => true).catch(() => false); } catch (_) {}
      }
      return resolved();
    },
    rewarded() {
      if (platform === "crazygames") return crazyAd("rewarded");
      if (platform === "poki" && sdk) {
        try { return sdk.rewardedBreak().then((granted) => Boolean(granted)).catch(() => false); } catch (_) {}
      }
      return resolved();
    },
    localFallback: noop,
  };
})(window);
