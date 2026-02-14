from model.command import Command


def test_command_from_string():
    command = Command.from_string("echo Hello World")
    assert command.internal_representation == ["echo", "Hello", "World"]
    assert command.command == "echo"
    assert command.get_full_command() == "echo Hello World"


def test_command_constructor():
    command = Command(["ls", "-l", "/home"])
    assert command.internal_representation == ["ls", "-l", "/home"]
    assert command.command == "ls"
    assert command.get_full_command() == "ls -l /home"


def test_composed_command():
    command1 = Command.from_string("echo Hello")
    composed_command = Command(["run", command1])
    assert composed_command.internal_representation == ["run", command1]
    assert composed_command.command == "run"
    assert composed_command.get_full_command() == "run echo Hello"
    assert composed_command.get_chain_command() == ["run", "echo", "Hello"]


def test_replace_command():
    command = Command.from_string("echo Hello World")
    command.replace_command("ls")
    assert command.internal_representation == ["ls", "Hello", "World"]
    assert command.command == "ls"
    assert command.get_full_command() == "ls Hello World"


def test_replace_args():
    command = Command.from_string("echo Hello World")
    command.replace_args("Goodbye Everyone")
    assert command.internal_representation == ["echo", "Goodbye", "Everyone"]
    assert command.command == "echo"
    assert command.get_full_command() == "echo Goodbye Everyone"
