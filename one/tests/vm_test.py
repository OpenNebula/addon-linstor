from one import vm


def test_create_vm():
    test_name = "test"
    test_vm = vm.Create(test_name)

    assert test_vm.name == test_name
