define("ace/mode/timeline", ["require", "exports", "module", "ace/lib/oop", "ace/mode/text", "ace/mode/text_highlight_rules"], 
    function(require, exports, module) {
        var oop = require("ace/lib/oop");
        var TextMode = require("ace/mode/text").Mode;
        var TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;
        
        var TimelineHighlightRules = function() {
            this.$rules = {
                "start": [
                    {
                        // Match timestamps in square brackets, e.g. [19:58:12.174]
                        token: "constant.numeric.timestamp",
                        regex: "\\[\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?\\]"
                    },
                    {
                        // Match the object name pattern: <<object>>
                        // Group 1: the opening << (styled as punctuation)
                        // Group 2: the object name (styled as ace-timeline-object)
                        // Group 3: the closing >> (styled as punctuation)
                        token: ["punctuation.operator", "ace-timeline-object", "punctuation.operator"],
                        regex: "(<<)([^>]+)(>>)"
                    },
                    {
                        // Fallback rule: match any characters until a timestamp or << is found.
                        token: "text",
                        regex: "[^\\[<]+"
                    },
                    {
                        // Ensure we consume any single remaining character.
                        token: "text",
                        regex: "."
                    }
                ]
            };
            this.normalizeRules();
        };
        oop.inherits(TimelineHighlightRules, TextHighlightRules);
        
        var Mode = function() {
            this.HighlightRules = TimelineHighlightRules;
        };
        oop.inherits(Mode, TextMode);
        
        (function() {
            this.lineCommentStart = "";
            this.$id = "ace/mode/timeline";
        }).call(Mode.prototype);
        
        exports.Mode = Mode;
    });
    