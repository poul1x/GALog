from .tree_model import CustomTreeModel, TreeItem


def test_standard_item_model(qtmodeltester):
    model = CustomTreeModel(TreeItem(["Name", "Val"]), None)
    items = [TreeItem(["aaa", i]) for i in range(4)]
    items[0].addChild(TreeItem(["bbb", "ccc"]))
    model.setItems(items)
    qtmodeltester.check(model)
