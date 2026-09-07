(function () {
  "use strict";

  var labels = {
    en: "Choose language",
    zh: "选择语言",
    "zh-hans": "选择语言",
    "zh-hant": "選擇語言",
    ja: "言語を選ぶ",
    fr: "Choisir la langue",
    de: "Sprache wählen",
    es: "Elegir idioma",
    ko: "언어 선택"
  };

  function documentLanguage() {
    var language = (document.documentElement.lang || "en").toLowerCase();
    return labels[language] ? language : language.split("-")[0];
  }

  function storedLanguageFrom(node) {
    var handler = node.getAttribute("onclick") || "";
    var match = handler.match(/setItem\(\s*['"]nd_lang['"]\s*,\s*['"]([^'"]+)['"]\s*\)/);
    return match ? match[1] : "";
  }

  function enhance(toggle) {
    if (toggle.classList.contains("lang-select-menu")) return;

    var choices = Array.prototype.slice.call(toggle.querySelectorAll(".lang-btn"));
    if (!choices.length) return;

    var select = document.createElement("select");
    var currentLanguage = document.documentElement.getAttribute("data-lang") || "";
    var selectedIndex = -1;

    select.className = "lang-select";
    select.setAttribute("aria-label", labels[documentLanguage()] || labels.en);

    choices.forEach(function (choice, index) {
      var option = document.createElement("option");
      var inlineLanguage = choice.getAttribute("data-lang") || "";
      var href = choice.getAttribute("href") || "";

      option.textContent = choice.textContent.trim();
      option.value = String(index);

      if (inlineLanguage) {
        option.dataset.inlineLanguage = inlineLanguage;
      } else if (href) {
        option.dataset.href = href;
        option.dataset.storedLanguage = storedLanguageFrom(choice);
      }

      if (
        choice.classList.contains("active") ||
        (inlineLanguage && inlineLanguage === currentLanguage)
      ) {
        selectedIndex = index;
      }

      select.appendChild(option);
    });

    if (selectedIndex < 0) {
      selectedIndex = choices.findIndex(function (choice) {
        return choice.getAttribute("data-lang") === "zh";
      });
    }
    select.selectedIndex = selectedIndex < 0 ? 0 : selectedIndex;

    select.addEventListener("change", function () {
      var option = select.options[select.selectedIndex];
      var inlineLanguage = option.dataset.inlineLanguage;
      var href = option.dataset.href;

      if (inlineLanguage) {
        document.documentElement.setAttribute("data-lang", inlineLanguage);
        document.documentElement.lang = inlineLanguage === "zh" ? "zh-Hans" : inlineLanguage;
        localStorage.setItem("nd_lang", inlineLanguage);
        return;
      }

      if (option.dataset.storedLanguage) {
        localStorage.setItem("nd_lang", option.dataset.storedLanguage);
      }
      if (href) window.location.assign(href);
    });

    var chevron = document.createElement("span");
    chevron.className = "lang-select-chevron";
    chevron.setAttribute("aria-hidden", "true");
    chevron.textContent = "⌄";

    toggle.textContent = "";
    toggle.classList.add("lang-select-menu");
    toggle.appendChild(select);
    toggle.appendChild(chevron);
  }

  function init() {
    document.querySelectorAll(".lang-toggle").forEach(enhance);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
