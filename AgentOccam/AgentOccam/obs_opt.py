import re
from browser_env.processors import TreeNode
from functools import partial

RETAINED_PROPERTIES = ["required", "disabled", "checked", "valuemin", "valuemax", "valuetext", "selected", "page_dialog_message"]
UNWANTED_PROPERTIES = ["focused", "autocomplete", "hasPopup", "expanded", "multiselectable", "orientation", "controls"]
UNINTERACTIVE_ROLES = ["StaticText", "LabelText", "main", "heading", "LayoutTable", "tabpanel", "LayoutTableRow", "LayoutTableCell", "time", "list", "contentinfo", "table", "row", "rowheader", "columnheader", "gridcell", "caption", "DescriptionList", "DescriptionListTerm", "DescriptionListDetail", "RootWebArea", "rowgroup", "alert"]
ROLE_REPLACEMENT_DICT = {
    "StaticText": "text",
    "LabelText": "text",
    # "caption": "text",
    # "generic": "text"
}

def parse_text_to_tree(text):
    lines = text.split('\n')

    root = None
    parent_stack = {}

    for line in lines:
        if line.strip() == "":
            continue
        line_strip = line.strip()
        line_parts = line_strip.split(' ')
        id = line_parts[0][1:-1]
        type = line_parts[1]
        text = ' '.join(line_parts[2:])
        level = 0
        for char in line:
            if char == '\t':
                level += 1
            else:
                break

        node = TreeNode(id, type, text, level)

        if line.startswith('\t'):
            parent_stack[level].add_child(node)
        else:
            root = node

        parent_stack[level+1] = node

    return root

def remove_unwanted_characters(text):
    text = text.replace('\xa0', ' ')
    cleaned_text = re.sub(r'[^\w\s,.!?;:\-\'\"()&/\u2019@]+', '', text, flags=re.UNICODE)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text.strip()

def search_node_by_id(node, target_id):
    if node.node_id == target_id:
        return node
    for child in node.children:
        result = search_node_by_id(child, target_id)
        if result:
            return result
    return None

def action_replace_node_role(node:TreeNode, role_replacement_dict:dict):
    if node.role in role_replacement_dict.keys():
        node.role = role_replacement_dict[node.role]

def action_remove_unwanted_characters(node:TreeNode):
    node.name = remove_unwanted_characters(node.name)

def action_remove_unwanted_properties(node:TreeNode):
    if node.has_properties():
        node.properties = {p: node.properties[p] for p in node.properties.keys() if p not in UNWANTED_PROPERTIES}
        if node.parent and node.parent.role=="row" and not node.properties["required"]:
            del node.properties["required"]
        if len(node.properties) == 0:
            node.properties = None

def action_remove_redundant_statictext_node(node:TreeNode):
    if not node.visible:
        return
    if not (node.all_children_invisible() and node.role in ["StaticText", "LabelText", "caption"]):
        return
    if (not node.name) or (node.parent and node.name in node.parent.name) or (node.parent and any(node.name in sibling.name for sibling in node.siblings())):
        node.visible = False

def action_merge_statictext_to_parent(node:TreeNode):
    if not node.visible:
        return
    if not (node.all_children_invisible() and node.role in ["StaticText", "LabelText", "caption"]):
        return
    if node.parent and not node.parent.name and len(node.parent.children) == 1:
        node.parent.name = node.name
        node.visible = False

def action_merge_menuitem_and_option(node:TreeNode):
    if not node.visible:
        return
    if not ((node.visible_children() and all(c.role=="menuitem" for c in node.visible_children())) or (node.visible_children() and all(c.role=="option" for c in node.visible_children()))):
        return
    if node.visible_children()[0].role == "menuitem":
        if not node.name.strip():
            node.name = "; ".join([action_return_visible_node(c).strip()[len("menuitem "):] for c in node.visible_children()])
        else:
            node.name += ": " + "; ".join([action_return_visible_node(c).strip()[len("menuitem "):] for c in node.visible_children()])
    elif node.visible_children()[0].role == "option":
        if not node.name.strip():
            node.name = "; ".join([action_return_visible_node(c).strip()[len("option "):] for c in node.visible_children()])
        else:
            node.name += ": " + "; ".join([action_return_visible_node(c).strip()[len("option "):] for c in node.visible_children()])
    for c in node.visible_children():
        c.visible = False

def action_merge_description_list(node:TreeNode):
    if not node.visible:
        return
    def reformat_sublist(current_list_term_buffer):
        if len(current_list_term_buffer) > 1:
            list_term_node_appended_name = []
            for n in current_list_term_buffer[1:]:
                list_term_node_appended_name.append(n.name)
                n.visible = False
            current_list_term_buffer[0].name += ": " + "; ".join(list_term_node_appended_name)
            
    if not node.role == "DescriptionList":
        return
    for child in node.visible_children():
        if child.role == "DescriptionListDetail" and not child.name and len(child.visible_children()) == 1:
            child.name = action_return_visible_node(child.visible_children()[0]).strip()
            child.visible_children()[0].visible = False
    list_term_buffer = []
    for child in node.visible_children():
        if child.role == "DescriptionListTerm" and child.all_children_invisible():
            reformat_sublist(current_list_term_buffer=list_term_buffer)
            list_term_buffer = [child]
        elif child.role == "DescriptionListDetail" and child.all_children_invisible() and list_term_buffer:
            list_term_buffer.append(child)
        elif child.role == "DescriptionListDetail" and not child.all_children_invisible():
            list_term_buffer = []
        else:
            reformat_sublist(current_list_term_buffer=list_term_buffer)
            list_term_buffer = []
        reformat_sublist(current_list_term_buffer=list_term_buffer)

def action_remove_image(node:TreeNode):
    if not node.visible:
        return
    if node.all_children_invisible() and (node.role=="img" or node.name=="Image"):
        node.visible = False

def action_set_invisible(node:TreeNode):
    node.visible = False

def action_set_visible(node:TreeNode):
    node.visible = True

def action_set_visible_if_with_name(node:TreeNode):
    if node.name:
        node.visible = True

def action_reformat_table(node:TreeNode):
    if not node.visible:
        return
    def merge_gridcell(gridcell_node:TreeNode):
        if gridcell_node.role not in ["gridcell", "columnheader", "rowheader", "LayoutTableCell"] or not gridcell_node.visible:
            return
        gridcell_buffer = []
        parse_node_descendants(gridcell_node, action_return_visible_node, gridcell_buffer)
        if len(gridcell_buffer) == 1:
            return
        gridcell_buffer = [s.strip() for s in gridcell_buffer]
        if gridcell_node.name:
            gridcell_node.name += "\t" + "\t".join(gridcell_buffer[1:])
        else:
            gridcell_node.name = "\t".join(gridcell_buffer[1:])
        parse_node_descendants(gridcell_node, action_set_invisible)
        gridcell_node.visible = True

    try:
        if node.role == "table":

            def reformat_subtable(row_list, current_table_children):
                import copy
                new_table_children = copy.deepcopy(current_table_children)
                if row_list:
                    # if row_list[0].children[0].role == "columnheader":
                    if any(row_0_child.role == "columnheader" for row_0_child in row_list[0].children):
                        if new_table_children and any(n.visible for n in new_table_children):
                            new_table_children.append(TreeNode(node_id=row_list[0].node_id, role="row", name="", depth=row_list[0].depth))
                        for i, row in enumerate(row_list):
                            new_role_name = []
                            for row_element in row.children:
                                new_role_name.append(row_element.name)
                            new_table_children.append(TreeNode(node_id=row.node_id, role="row", name="| "+" | ".join(new_role_name)+" |", depth=row.depth))
                            if i == 0 and len(row_list) > 1:
                                new_table_children.append(TreeNode(node_id=row.node_id, role="row", name="| "+" | ".join(["---"]*len(new_role_name))+" |", depth=row.depth))
                    elif row_list[0].children[0].role == "rowheader":
                        if new_table_children and any(n.visible for n in new_table_children):
                            new_table_children.append(TreeNode(node_id=row_list[0].node_id, role="row", name="", depth=row_list[0].depth))
                        titles = [r.children[0].name for r in row_list]
                        values = [r.children[1].name for r in row_list]
                        new_table_children.append(TreeNode(node_id=row_list[0].node_id, role="row", name="| "+" | ".join(titles)+" |", depth=row_list[0].depth))
                        new_table_children.append(TreeNode(node_id=row_list[0].node_id, role="row", name="| "+" | ".join(["---"]*len(titles))+" |", depth=row_list[0].depth))
                        new_table_children.append(TreeNode(node_id=row_list[0].node_id, role="row", name="| "+" | ".join(values)+" |", depth=row_list[0].depth))
                    elif row_list[0].children[0].role == "gridcell":
                        if new_table_children and any(n.visible for n in new_table_children):
                            new_table_children.append(TreeNode(node_id=row_list[0].node_id, role="row", name="", depth=row_list[0].depth))
                        for row in row_list:
                            new_table_children.append(TreeNode(node_id=row.node_id, role="row", name="| "+" | ".join([row_element.name for row_element in row.children])+" |", depth=row.depth))
                    else:
                        raise NotImplementedError("Unrecognized table format.")
                return new_table_children
            
            new_table_children = []
            row_list = []
            row_mode = False
            for child in node.children:
                if child.role == "row":
                    for row_element in child.visible_children(): # TODO: Visible?
                        merge_gridcell(row_element)

                # if child.role == "row" and child.children[0].role == "columnheader":
                if child.role == "row" and any(row_child.role == "columnheader" for row_child in child.children):
                    row_list = [child]
                    row_mode = False
                elif child.role == "row" and child.children[0].role == "rowheader":
                    if row_mode:
                        row_list.append(child)
                    else:
                        new_table_children = reformat_subtable(row_list=row_list, current_table_children=new_table_children)
                        row_list = [child]
                    row_mode = True
                elif child.role == "row" and child.children[0].role == "gridcell":
                    row_list.append(child)
                    row_mode = False
                elif child.role != "row":
                    new_table_children = reformat_subtable(row_list=row_list, current_table_children=new_table_children)
                    if child.role == "rowgroup":
                        for grandchild in child.visible_children(): # grandchild: row
                            for row_element in grandchild.visible_children(): # TODO: Visible?
                                merge_gridcell(row_element)
                        child.children = reformat_subtable(row_list=child.children, current_table_children=[])
                    new_table_children.append(child)
                    row_list = []
                else:
                    raise NotImplementedError()
            new_table_children = reformat_subtable(row_list=row_list, current_table_children=new_table_children)
            node.children = new_table_children
        elif node.role == "LayoutTable":
            def merge_adjacent_text_nodes(nodes):
                if not nodes:
                    return []

                merged_nodes = []
                current_node = nodes[0]

                for i in range(1, len(nodes)):
                    if current_node.visible and current_node.role in ["LayoutTableCell", "StaticText", "generic"]+list(set(ROLE_REPLACEMENT_DICT.values())) and nodes[i].visible and nodes[i].role in ["LayoutTableCell", "StaticText", "generic"]+list(set(ROLE_REPLACEMENT_DICT.values())):
                        current_node.role = ROLE_REPLACEMENT_DICT["StaticText"]
                        current_node.name += " " + nodes[i].name  # Merge text values
                        nodes[i].visible = False
                    else:
                        merged_nodes.append(current_node)
                        current_node = nodes[i]

                merged_nodes.append(current_node)

                return merged_nodes
            def dfs_merge_text(n:TreeNode):
                if not n.children:
                    return
                for c in n.children:
                    dfs_merge_text(c)
                n.children = merge_adjacent_text_nodes(n.children)
                if len(n.visible_children()) == 1 and n.visible_children()[0].role in ["LayoutTableCell", "StaticText", "generic"]+list(set(ROLE_REPLACEMENT_DICT.values())) and n.role in ["LayoutTableCell", "StaticText", "generic"]+list(set(ROLE_REPLACEMENT_DICT.values())):
                    n.name += "\t" + n.visible_children()[0].name
                    n.visible_children()[0].visible = False
                if n.role == "LayoutTableRow":
                    for row_element in n.children:
                        if row_element.visible and row_element.children:
                            for sub_element in row_element.children:
                                if sub_element.visible:
                                    node_str = action_return_visible_node(sub_element).strip()
                                    row_element.name += f"\t{node_str}"
                            row_element.children = []
                    n.name = "| " + " | ".join([c.name for c in n.children if c.visible]) + " |" # TODO: Visible?
                    for row_element in n.children:
                        row_element.visible = False
            dfs_merge_text(node)
    except Exception as e:
        print("Table reformatting error:", e)

def action_merge_duplicated_headings(node:TreeNode):
    if not node.visible or not node.all_children_invisible() or not node.parent or node.visible_siblings():
        return
    if node.role=="heading" and node.parent.role not in UNINTERACTIVE_ROLES and node.name == node.parent.name:
        node.visible = False
    if node.parent.role=="heading" and node.role not in UNINTERACTIVE_ROLES and node.name == node.parent.name:
        node.parent.node_id = node.node_id
        node.parent.role = node.role
        node.parent.properties = node.properties
        node.parent.children = node.children
        node.visible = False

def action_print_tree(node:TreeNode):
    print("\t" * node.depth + f"{node.visible} {node.depth} [{node.node_id}] {node.role}: {node.name}")

def action_return_visible_node(node:TreeNode, intent_bias=0, mode="concise", **kwargs):
    if not node.visible:
        return None
    if mode == "concise":
        node_str = node.role
        hidden_roles = UNINTERACTIVE_ROLES+list(set(ROLE_REPLACEMENT_DICT.values()))
        if "[" in node.name and "hidden_roles" in kwargs.keys():
            hidden_roles += kwargs["hidden_roles"]
        if node.role not in hidden_roles:
            node_str += f" [{node.node_id}]"    
    elif mode == "verbose":
        node_str = f"{node.role} [{node.node_id}]"
    elif mode == "name_only":
        node_str = node.role
    elif mode == "name_retained_id_only":
        node_str = node.role
        retained_ids = kwargs.get("retained_ids", [])
        if node.node_id in retained_ids:
            node_str += f" [{node.node_id}]"
    
    if node.name:
        node_str += f" {repr(node.name)}"
    if node.has_properties():
        for p in node.properties:
            p_value = node.properties[p]
            node_str += f" [{p}: {p_value}]"
    return "\t" * (node.depth-intent_bias) + node_str

def parse_node_siblings(node:TreeNode, action=action_print_tree, tree_buffer=[]):
    for sibling in node.siblings():
        res_action = action(sibling)
        if res_action:
            tree_buffer.append(res_action)

def parse_node_ancestors(node:TreeNode, action=action_print_tree, tree_buffer=[]):
    res_action = action(node)
    if res_action:
        tree_buffer.append(res_action)
    if node.parent:
        parse_node_ancestors(node=node.parent, action=action, tree_buffer=tree_buffer)

def parse_node_descendants(node:TreeNode, action=action_print_tree, tree_buffer=[]):
    res_action = action(node)
    if res_action:
        tree_buffer.append(res_action)
    for child in node.children:
        parse_node_descendants(node=child, action=action, tree_buffer=tree_buffer)

def prune_tree_fuzzy_node(node:TreeNode): # TODO: Bugs!!!
    if not node.children:
        return
    
    # Iterate over the children in reverse order to safely remove nodes
    fuzzy_children = []
    for child in reversed(node.children):
        prune_tree_fuzzy_node(child)
        if child.all_children_invisible() and not child.is_differentiable(strict=True):
            fuzzy_children.append(child)
    for child in fuzzy_children:
        child.visible = False

def translate_node_to_str(node: TreeNode, mode="concise", **kwargs):
    tree_buffer = []
    parse_node_descendants(node, partial(action_return_visible_node, intent_bias=node.depth, mode=mode, **kwargs), tree_buffer=tree_buffer)
    return "\n".join(tree_buffer[:1000])

def construct_new_DOM_with_visible_nodes(DOM_root:TreeNode):
    def dfs(node:TreeNode):
        if not node.visible:
            return None
        if not node.visible_children():
            return node.copy()
        new_self = node.copy()
        for child in node.visible_children():
            new_child = dfs(child)
            if new_child:
                new_self.add_child(new_child)
        return new_self
    new_DOM_Root = dfs(DOM_root)
    return new_DOM_Root

def prune_tree(objective, root_node, mode="str"):
    root_node_copy = construct_new_DOM_with_visible_nodes(root_node)
    parse_node_descendants(root_node_copy, action_remove_unwanted_characters)
    parse_node_descendants(root_node_copy, action_remove_unwanted_properties)
    parse_node_descendants(root_node_copy, action_remove_redundant_statictext_node)
    parse_node_descendants(root_node_copy, action_remove_image)
    prune_tree_fuzzy_node(root_node_copy)
    parse_node_descendants(root_node_copy, action_remove_image)
    parse_node_descendants(root_node_copy, action_merge_statictext_to_parent)
    parse_node_descendants(root_node_copy, action_remove_redundant_statictext_node)
    parse_node_descendants(root_node_copy, partial(action_replace_node_role, role_replacement_dict=ROLE_REPLACEMENT_DICT))
    parse_node_descendants(root_node_copy, action_merge_menuitem_and_option)
    parse_node_descendants(root_node_copy, action_merge_description_list)
    parse_node_descendants(root_node_copy, action_reformat_table)
    parse_node_descendants(root_node_copy, action_merge_duplicated_headings)

    if mode == "str":
        browser_content = translate_node_to_str(node=root_node_copy, mode="concise")
    elif mode == "node":
        browser_content = construct_new_DOM_with_visible_nodes(root_node_copy)
    return browser_content

def contains_keyword(title, keyword):
    return keyword in title.lower()
