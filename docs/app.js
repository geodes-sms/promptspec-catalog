(function () {
  "use strict";

  var CATALOG_PATHS = ["catalog/patterns.json", "../catalog/patterns.json"];

  var CATEGORY_ORDER = [
    "IN_CONTEXT_LEARNING",
    "REASONING",
    "OUTPUT_CONTROL",
    "CONTEXT_CONTROL",
    "META_DIRECTIVES"
  ];

  var CATEGORY_LABELS = {
    IN_CONTEXT_LEARNING: "In-Context Learning",
    REASONING: "Reasoning",
    OUTPUT_CONTROL: "Output Control",
    CONTEXT_CONTROL: "Context Control",
    META_DIRECTIVES: "Meta-Directives"
  };

  var CATEGORY_PALETTES = {
    IN_CONTEXT_LEARNING: {
      accent: "#0072B2",
      soft: "#E8F3F8",
      ink: "#004F7C"
    },
    REASONING: {
      accent: "#D55E00",
      soft: "#FBEFE7",
      ink: "#8C3D00"
    },
    OUTPUT_CONTROL: {
      accent: "#009E73",
      soft: "#E7F5F0",
      ink: "#006B4E"
    },
    CONTEXT_CONTROL: {
      accent: "#7A5195",
      soft: "#F2ECF5",
      ink: "#573766"
    },
    META_DIRECTIVES: {
      accent: "#A43A75",
      soft: "#F8EAF2",
      ink: "#702650"
    },
    UNCATEGORIZED: {
      accent: "#66727F",
      soft: "#F0F2F4",
      ink: "#3E4A54"
    }
  };

  var SUBCATEGORY_PALETTES = {
    "Zero-shot": { accent: "#0072B2", soft: "#E8F3F8", ink: "#004F7C" },
    "Few-shot": { accent: "#56B4E9", soft: "#EDF7FC", ink: "#285F7A" },
    "Chain-of-Thought": { accent: "#D55E00", soft: "#FBEFE7", ink: "#8C3D00" },
    Planning: { accent: "#E69F00", soft: "#FCF4DF", ink: "#765100" },
    Decomposition: { accent: "#B66D12", soft: "#F8F0E5", ink: "#70410A" },
    "Output formatting": { accent: "#009E73", soft: "#E7F5F0", ink: "#006B4E" },
    Procedural: { accent: "#2A8F75", soft: "#E9F4F1", ink: "#1B5F4E" },
    "Schema specification": { accent: "#1B7F8C", soft: "#E8F3F5", ink: "#155661" },
    Verification: { accent: "#4E8B57", soft: "#EDF4EE", ink: "#315A38" },
    "Context grounding": { accent: "#7A5195", soft: "#F2ECF5", ink: "#573766" },
    "Input semantics": { accent: "#8C6BB1", soft: "#F3EFF8", ink: "#5D4775" },
    "Role & perspective": { accent: "#6F5AA8", soft: "#F0EEF7", ink: "#493B70" },
    Enhancement: { accent: "#A43A75", soft: "#F8EAF2", ink: "#702650" },
    Interaction: { accent: "#C44E52", soft: "#F9ECEC", ink: "#7D3033" },
    Refinement: { accent: "#B24C8A", soft: "#F7EBF3", ink: "#74315A" },
    Uncategorized: { accent: "#66727F", soft: "#F0F2F4", ink: "#3E4A54" }
  };

  var COMPONENT_LABELS = {
    PROFILE_ROLE: "Profile/Role",
    DIRECTIVE: "Directive",
    CONTEXT: "Context",
    PROCEDURAL_STEPS: "Procedural Steps",
    EXAMPLES: "Examples",
    OUTPUT_FORMAT: "Output Format/Style",
    CONSTRAINTS: "Constraints"
  };

  var state = {
    patterns: [],
    filtered: [],
    search: "",
    category: "",
    subcategory: "",
    expanded: {}
  };

  var elements = {
    count: document.getElementById("pattern-count"),
    tree: document.getElementById("taxonomy-tree"),
    empty: document.getElementById("empty-state"),
    message: document.getElementById("load-message"),
    search: document.getElementById("search-input"),
    category: document.getElementById("category-filter"),
    subcategory: document.getElementById("subcategory-filter"),
    clear: document.getElementById("clear-filters")
  };

  function text(value) {
    if (value === null || value === undefined) {
      return "";
    }
    if (Array.isArray(value)) {
      return value.filter(Boolean).join(", ");
    }
    return String(value);
  }

  function labelCategory(value) {
    return CATEGORY_LABELS[value] || text(value);
  }

  function labelComponent(value) {
    return COMPONENT_LABELS[value] || text(value);
  }

  function slug(value) {
    return text(value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  }

  function setMessage(message, isError) {
    if (!message) {
      elements.message.classList.add("hidden");
      elements.message.textContent = "";
      return;
    }
    elements.message.textContent = message;
    elements.message.classList.remove("hidden");
    elements.message.classList.toggle("error", Boolean(isError));
  }

  function createElement(tag, className, content) {
    var element = document.createElement(tag);
    if (className) {
      element.className = className;
    }
    if (content !== undefined && content !== null) {
      element.textContent = content;
    }
    return element;
  }

  function applyPalette(element, palette) {
    element.style.setProperty("--node-accent", palette.accent);
    element.style.setProperty("--node-soft", palette.soft);
    element.style.setProperty("--node-ink", palette.ink);
  }

  function categoryPalette(category) {
    return CATEGORY_PALETTES[category] || CATEGORY_PALETTES.UNCATEGORIZED;
  }

  function subcategoryPalette(subcategory, category) {
    return SUBCATEGORY_PALETTES[subcategory] || categoryPalette(category);
  }

  function buttonNode(label, count, level, key, expanded, palette) {
    var button = createElement("button", "tree-toggle level-" + level);
    var panelId = "panel-" + slug(key);
    button.type = "button";
    button.dataset.toggleKey = key;
    button.setAttribute("aria-expanded", expanded ? "true" : "false");
    button.setAttribute("aria-controls", panelId);
    if (palette) {
      applyPalette(button, palette);
    }

    button.appendChild(createElement("span", "toggle-mark", expanded ? "-" : "+"));
    button.appendChild(createElement("span", "node-label", label));
    if (count !== null && count !== undefined) {
      button.appendChild(createElement("span", "node-count", String(count)));
    }
    return button;
  }

  function panelNode(key, expanded) {
    var panel = createElement("div", "tree-panel");
    panel.id = "panel-" + slug(key);
    panel.hidden = !expanded;
    return panel;
  }

  function patternHaystack(pattern) {
    return [
      pattern.name,
      pattern.description,
      pattern.subcategory,
      pattern.category,
      pattern.componentTypes,
      pattern.detectionInstruction,
      pattern.notes
    ]
      .map(text)
      .join(" ")
      .toLowerCase();
  }

  function patternMatches(pattern) {
    var query = state.search.trim().toLowerCase();
    if (state.category && pattern.category !== state.category) {
      return false;
    }
    if (state.subcategory && pattern.subcategory !== state.subcategory) {
      return false;
    }
    return !query || patternHaystack(pattern).indexOf(query) !== -1;
  }

  function sortedCategories() {
    var available = {};
    state.patterns.forEach(function (pattern) {
      available[pattern.category || "UNCATEGORIZED"] = true;
    });
    return CATEGORY_ORDER.filter(function (category) {
      return available[category];
    }).concat(
      Object.keys(available)
        .filter(function (category) {
          return CATEGORY_ORDER.indexOf(category) === -1;
        })
        .sort()
    );
  }

  function sortedSubcategories() {
    var available = {};
    state.patterns.forEach(function (pattern) {
      if (!state.category || pattern.category === state.category) {
        available[pattern.subcategory || "Uncategorized"] = true;
      }
    });
    return Object.keys(available).sort(function (a, b) {
      return a.localeCompare(b);
    });
  }

  function replaceOptions(select, defaultLabel, options, selectedValue, labeler) {
    select.textContent = "";
    var defaultOption = createElement("option", "", defaultLabel);
    defaultOption.value = "";
    select.appendChild(defaultOption);
    options.forEach(function (value) {
      var option = createElement("option", "", labeler ? labeler(value) : value);
      option.value = value;
      select.appendChild(option);
    });
    select.value = selectedValue;
  }

  function updateFilterOptions() {
    replaceOptions(
      elements.category,
      "All categories",
      sortedCategories(),
      state.category,
      labelCategory
    );

    var subcategories = sortedSubcategories();
    if (state.subcategory && subcategories.indexOf(state.subcategory) === -1) {
      state.subcategory = "";
    }
    replaceOptions(
      elements.subcategory,
      "All subcategories",
      subcategories,
      state.subcategory
    );
  }

  function groupPatterns(patterns) {
    var grouped = {};
    patterns.forEach(function (pattern) {
      var category = pattern.category || "UNCATEGORIZED";
      var subcategory = pattern.subcategory || "Uncategorized";
      grouped[category] = grouped[category] || {};
      grouped[category][subcategory] = grouped[category][subcategory] || [];
      grouped[category][subcategory].push(pattern);
    });
    Object.keys(grouped).forEach(function (category) {
      Object.keys(grouped[category]).forEach(function (subcategory) {
        grouped[category][subcategory].sort(function (a, b) {
          return text(a.name).localeCompare(text(b.name));
        });
      });
    });
    return grouped;
  }

  function countCategory(subgroups) {
    return Object.keys(subgroups).reduce(function (total, subcategory) {
      return total + subgroups[subcategory].length;
    }, 0);
  }

  function isExpanded(key, defaultValue, forceExpanded) {
    if (forceExpanded) {
      return true;
    }
    if (Object.prototype.hasOwnProperty.call(state.expanded, key)) {
      return state.expanded[key];
    }
    return defaultValue;
  }

  function renderComponentTags(pattern) {
    var tags = createElement("ul", "tag-list");
    (pattern.componentTypes || []).forEach(function (component) {
      tags.appendChild(createElement("li", "tag", labelComponent(component)));
    });
    return tags;
  }

  function renderPatternDetails(pattern) {
    var details = createElement("div", "pattern-details");

    var componentBlock = createElement("div", "detail-block");
    componentBlock.appendChild(createElement("span", "detail-label", "Component use"));
    componentBlock.appendChild(renderComponentTags(pattern));
    details.appendChild(componentBlock);

    var description = createElement("div", "detail-block");
    description.appendChild(createElement("span", "detail-label", "Description"));
    description.appendChild(createElement("p", "meta-text", text(pattern.description)));
    details.appendChild(description);

    if (pattern.formalization) {
      var formalization = createElement("div", "detail-block");
      formalization.appendChild(createElement("span", "detail-label", "Formalization"));
      formalization.appendChild(createElement("pre", "", text(pattern.formalization)));
      details.appendChild(formalization);
    }

    return details;
  }

  function renderPattern(pattern, queryActive) {
    var key = "pattern:" + pattern.id;
    var expanded = isExpanded(key, false, queryActive);
    var item = createElement("div", "tree-item pattern-item");
    item.appendChild(buttonNode(text(pattern.name), null, "pattern", key, expanded));

    var panel = panelNode(key, expanded);
    panel.appendChild(renderPatternDetails(pattern));
    item.appendChild(panel);
    return item;
  }

  function renderTree() {
    state.filtered = state.patterns.filter(patternMatches);
    var filtersActive = Boolean(
      state.search.trim() || state.category || state.subcategory
    );
    var grouped = groupPatterns(state.filtered);
    var categories = CATEGORY_ORDER.filter(function (category) {
      return grouped[category];
    }).concat(
      Object.keys(grouped)
        .filter(function (category) {
          return CATEGORY_ORDER.indexOf(category) === -1;
        })
        .sort()
    );

    elements.tree.textContent = "";
    categories.forEach(function (category) {
      var subgroups = grouped[category];
      var categoryKey = "category:" + category;
      var categoryExpanded = isExpanded(categoryKey, true, filtersActive);
      var categoryItem = createElement("section", "tree-item category-item");
      var categoryColors = categoryPalette(category);
      applyPalette(categoryItem, categoryColors);
      categoryItem.appendChild(
        buttonNode(
          labelCategory(category),
          countCategory(subgroups),
          "category",
          categoryKey,
          categoryExpanded,
          categoryColors
        )
      );

      var categoryPanel = panelNode(categoryKey, categoryExpanded);
      Object.keys(subgroups)
        .sort()
        .forEach(function (subcategory) {
          var patterns = subgroups[subcategory];
          var subcategoryKey = categoryKey + ":subcategory:" + subcategory;
          var subcategoryExpanded = isExpanded(
            subcategoryKey,
            false,
            filtersActive
          );
          var subcategoryItem = createElement("div", "tree-item subcategory-item");
          var subcategoryColors = subcategoryPalette(subcategory, category);
          applyPalette(subcategoryItem, subcategoryColors);
          subcategoryItem.appendChild(
            buttonNode(
              subcategory,
              patterns.length,
              "subcategory",
              subcategoryKey,
              subcategoryExpanded,
              subcategoryColors
            )
          );

          var subcategoryPanel = panelNode(subcategoryKey, subcategoryExpanded);
          patterns.forEach(function (pattern) {
            subcategoryPanel.appendChild(renderPattern(pattern, filtersActive));
          });
          subcategoryItem.appendChild(subcategoryPanel);
          categoryPanel.appendChild(subcategoryItem);
        });
      categoryItem.appendChild(categoryPanel);
      elements.tree.appendChild(categoryItem);
    });

    elements.empty.classList.toggle("hidden", state.filtered.length > 0);
    elements.count.textContent =
      state.filtered.length === state.patterns.length
        ? state.patterns.length + " patterns"
        : state.filtered.length + " of " + state.patterns.length + " patterns";
  }

  function wireControls() {
    document.querySelectorAll('a[aria-disabled="true"]').forEach(function (link) {
      link.addEventListener("click", function (event) {
        event.preventDefault();
      });
    });

    elements.search.addEventListener("input", function (event) {
      state.search = event.target.value;
      renderTree();
    });

    elements.category.addEventListener("change", function (event) {
      state.category = event.target.value;
      updateFilterOptions();
      renderTree();
    });

    elements.subcategory.addEventListener("change", function (event) {
      state.subcategory = event.target.value;
      renderTree();
    });

    elements.clear.addEventListener("click", function () {
      state.search = "";
      state.category = "";
      state.subcategory = "";
      elements.search.value = "";
      updateFilterOptions();
      renderTree();
      elements.search.focus();
    });

    elements.tree.addEventListener("click", function (event) {
      var button = event.target.closest("button[data-toggle-key]");
      if (!button) {
        return;
      }
      var key = button.dataset.toggleKey;
      state.expanded[key] = button.getAttribute("aria-expanded") !== "true";
      renderTree();
    });
  }

  function fetchCatalogFrom(paths) {
    var failures = [];

    function tryPath(index) {
      if (index >= paths.length) {
        throw new Error("Could not load catalog JSON. Tried: " + failures.join(", "));
      }

      return fetch(paths[index], { cache: "no-store" })
        .then(function (response) {
          if (!response.ok) {
            throw new Error(paths[index] + " returned " + response.status);
          }
          return response.json();
        })
        .catch(function (error) {
          failures.push(error.message);
          return tryPath(index + 1);
        });
    }

    return tryPath(0);
  }

  function init() {
    setMessage("Loading catalog from patterns.json...", false);
    fetchCatalogFrom(CATALOG_PATHS)
      .then(function (data) {
        if (!data || !Array.isArray(data.patterns)) {
          throw new Error("Catalog JSON did not contain a patterns array.");
        }
        state.patterns = data.patterns.slice();
        updateFilterOptions();
        wireControls();
        renderTree();
        setMessage("", false);
      })
      .catch(function (error) {
        elements.count.textContent = "Catalog unavailable";
        setMessage(
          "The interactive catalog could not be loaded. Read the JSON source or Markdown catalog from the repository instead. " +
            error.message,
          true
        );
      });
  }

  init();
})();
