To convert `fragment.html` into `switches.yaml` with the desired structure, you can use the following `yq` command. This command leverages `yq`'s ability to parse HTML and then transform the resulting YAML structure.

```bash
yq -px -oy fragment.html | \
yq \
'\
.tbody.tr[] | \
  {\
    id: ."+@id",\
    switch: (.td[0]."+content" | sub("(<a[^>]+><sup>[\d+]</sup></a>\s*|\s*⊗)", "") | trim),\
    description: (\
      .td[1].i |\
      select(. == "No description") |\
      "No description provided."\
    ) // (\
      .td[1]."+content" |\
      sub("<[^>]+>", "") |\
      trim |\
      select(. != "") // "No description provided."
    )\
    source_url: .td[1].a."+@href"
  }
' > switches.yaml
```

**Explanation of the command:**

1.  `yq -px -oy fragment.html`:
    *   `-p x`: Specifies the parser to use. `x` stands for XML/HTML, allowing `yq` to interpret `fragment.html` as an XML-like structure.
    *   `-o y`: Specifies the output format as YAML.
    *   This first part reads `fragment.html` and converts its HTML DOM into a YAML representation.

2.  `|`: This pipes the YAML output from the first `yq` command as input to the second `yq` command.

3.  `yq '...'`: This is the core transformation logic.
    *   `.tbody.tr[]`: This selects each `<tr>` element within the `<tbody>` section of the parsed HTML. The `[]` iterates over each item in the list.
    *   `{ ... }`: For each `<tr>` element, a new YAML object is constructed with the specified keys:
        *   `id: ."+@id"`: Extracts the `id` attribute of the `<tr>` element. `+@` is `yq`'s way of accessing attributes.
        *   `switch: (.td[0]."+content" | sub("(<a[^>]+><sup>[\d+]</sup></a>\s*|\s*⊗)", "") | trim)`:
            *   `.td[0]."+content"`: Gets the text content of the first `<td>` element (which contains the switch name).
            *   `sub("(<a[^>]+><sup>[\d+]</sup></a>\s*|\s*⊗)", "")`: Uses a regular expression to remove the `<sup>[number]</sup>` tags (and their surrounding `<a>` tags) and the `⊗` character, which are part of the raw switch name in the HTML.
            *   `trim`: Removes leading/trailing whitespace.
        *   `description: (...)`: This is a conditional logic block:
            *   `.td[1].i | select(. == "No description") | "No description provided."`: Checks if the second `<td>` contains an `<i>` tag with the exact content "No description". If true, the description is set to "No description provided.".
            *   `//`: This is `yq`'s "alternative value" operator. If the left side (the `<i>` tag check) does not produce a value (i.e., the condition is false), it falls back to the right side.
            *   `.td[1]."+content" | sub("<[^>]+>", "") | trim | select(. != "") // "No description provided."`: If the `<i>` tag condition is false, this part takes the `+content` of the second `<td>`, removes any remaining HTML tags (`<[^>]+>`), trims whitespace, and if the result is an empty string (`select(. != "")`), it defaults to "No description provided.".
        *   `source_url: .td[1].a."+@href"`: Extracts the `href` attribute of the `<a>` tag within the second `<td>` element.

4.  `> switches.yaml`: Redirects the final YAML output to a file named `switches.yaml`.