-- wikilinks.lua
-- Pandoc Lua filter that converts [[Note Title]] to HTML links.
-- Place this file in ~/KnowledgeVault/ alongside vault.py.
-- Update your ,c command in vimrc to include: --lua-filter=../wikilinks.lua
--
-- How it works:
--   [[Note Title]]           → looks for Note_Title.html in same or sibling folders
--   [[Note Title|link text]] → same but displays "link text" instead

local vault_path = os.getenv("HOME") .. "/KnowledgeVault"

-- Build a map of title → relative html path by scanning all .md files
local function build_title_map()
  local map = {}
  local handle = io.popen('find "' .. vault_path .. '" -name "*.md" 2>/dev/null')
  if not handle then return map end
  for filepath in handle:lines() do
    -- Extract title from frontmatter
    local f = io.open(filepath, "r")
    if f then
      local content = f:read("*a")
      f:close()
      local title = content:match("^%-%-%-.-\ntitle:%s*(.-)%s*\n")
      if not title then
        -- Fall back to filename stem
        title = filepath:match("([^/]+)%.md$")
        if title then title = title:gsub("_", " ") end
      end
      if title then
        -- Compute html path relative to vault
        local html_path = filepath:gsub("%.md$", ".html")
        -- Make relative to vault
        html_path = html_path:gsub(vault_path .. "/", "")
        map[title:lower()] = {
          title = title,
          html  = html_path,
        }
        -- Also index by filename stem for fallback
        local stem = filepath:match("([^/]+)%.md$")
        if stem then
          map[stem:lower()] = map[title:lower()]
          map[stem:lower():gsub("_", " ")] = map[title:lower()]
        end
      end
    end
  end
  handle:close()
  return map
end

local title_map = nil

-- Process inline code that looks like [[wikilink]]
function Str(elem)
  return elem
end

-- The main filter — intercepts raw strings and finds [[...]] patterns
function Para(elem)
  return elem
end

-- Process the AST to find and replace wikilinks in all inline elements
function Inlines(inlines)
  if title_map == nil then
    title_map = build_title_map()
  end

  local result = {}
  for _, inline in ipairs(inlines) do
    if inline.t == "Str" then
      local text = inline.text
      -- Check if this string contains [[ ]] patterns
      if text:find("%[%[") then
        -- Split on wikilink boundaries
        local pos = 1
        while pos <= #text do
          local s, e = text:find("%[%[.-%]%]", pos)
          if s then
            -- Text before the wikilink
            if s > pos then
              table.insert(result, pandoc.Str(text:sub(pos, s - 1)))
            end
            -- Extract wikilink content
            local inner = text:sub(s + 2, e - 2)
            local link_title, display = inner:match("^(.-)%|(.+)$")
            if not link_title then
              link_title = inner
              display = inner
            end
            -- Look up in title map
            local entry = title_map[link_title:lower()]
            if entry then
              -- Create a proper link
              local target = "/" .. entry.html
              table.insert(result, pandoc.Link(
                pandoc.Inlines({pandoc.Str(display)}),
                target,
                display
              ))
            else
              -- Not found — render as plain text with brackets
              table.insert(result, pandoc.Str("[[" .. display .. "]]"))
            end
            pos = e + 1
          else
            -- No more wikilinks
            table.insert(result, pandoc.Str(text:sub(pos)))
            break
          end
        end
      else
        table.insert(result, inline)
      end
    else
      table.insert(result, inline)
    end
  end
  return pandoc.Inlines(result)
end
