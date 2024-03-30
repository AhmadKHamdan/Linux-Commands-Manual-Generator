import xml.etree.ElementTree as ET
from xml.dom import minidom
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import glob
import os


class commandManualGenerator:
    def __init__(self):
        self.manual = []

    def readFile(self, inputFile):
        with open(inputFile, "r") as file:
            for commandName in file:
                commandName = commandName.strip()
                if commandName:
                    commandManual = CommandManual(commandName)
                    if commandManual not in self.manual:
                        self.manual.append(commandManual)

    def addCommand(self, commandName):
        if commandName:
            if not any(manual.commandName == commandName for manual in self.manual):
                commandManual = CommandManual(commandName)
                self.manual.append(commandManual)
                self.createCommandManual(commandManual)
            else:
                commandManual = CommandManual(commandName)
                self.createCommandManual(commandManual)

    def printManualsToTerminal(self):
        for manual in self.manual:
            manual.printManual()
            print("-" * 40)

    def createCommandManual(self, commandManual):
        XMLOutput = XmlSerializer.serializeOne(commandManual)
        with open(f"{commandManual.commandName}.xml", "w") as file:
            file.write(XMLOutput)

    def createCommandsManuals(self):
        # Generate individual command manuals
        for manual in self.manual:
            XMLOutput = XmlSerializer.serializeOne(manual)
            filePath = f"{manual.commandName}.xml"
            with open(f"{manual.commandName}.xml", "w") as file:
                file.write(XMLOutput)

        # Generate the combined manual
        XMLOutput_all = XmlSerializer.serializeAll(self.manual)
        with open("manual.xml", "w") as file:
            file.write(XMLOutput_all)


class CommandManual:
    def __init__(self, commandName):
        self.commandName = commandName
        self.description = ""
        self.version = ""
        self.exampleInput = ""
        self.exampleOutput = ""
        self.relatedCommands = []
        self.recommendedCommands = []
        self.generateManual()
        self.setUpRecommendations()

    def __eq__(self, other):
        if isinstance(other, CommandManual):
            return self.commandName == other.commandName
        return False

    def generateManual(self):
        descriptionLineNumber = count = 0

        # Getting the description of the command
        manual = subprocess.run(
            ["man", self.commandName], capture_output=True, text=True
        )
        manualLines = manual.stdout.splitlines()
        for i, line in enumerate(manualLines):
            if "DESCRIPTION" in line:
                descriptionLineNumber = i
                break
        self.description = manualLines[descriptionLineNumber + 1].strip()

        # Getting the version of the command
        self.version = subprocess.run(
            [self.commandName, "--version"], capture_output=True, text=True
        ).stdout.splitlines()[0]

        # Getting the examples for the command
        if self.commandName == "touch":
            self.exampleInput = "touch file.txt"
            self.exampleOutput = "Created file.txt"
            subprocess.run(["touch", "file.txt"])
        elif self.commandName == "echo":
            self.exampleInput = "echo 'hi\\nbye' > file.txt"
            self.exampleOutput = "Wrote hi\\nbye on file.txt"
            with open("file.txt", "w") as file:
                subprocess.run(["echo", "hi\nbye"], stdout=file, text=True)
        elif self.commandName == "cat":
            self.exampleInput = "cat file.txt"
            self.exampleOutput = subprocess.run(
                ["cat", "file.txt"], capture_output=True, text=True
            ).stdout.splitlines()
        elif self.commandName == "head":
            self.exampleInput = "head -1 file.txt"
            self.exampleOutput = subprocess.run(
                ["head", "-1", "file.txt"], capture_output=True, text=True
            ).stdout.strip()
        elif self.commandName == "tail":
            self.exampleInput = "tail -1 file.txt"
            self.exampleOutput = subprocess.run(
                ["tail", "-1", "file.txt"], capture_output=True, text=True
            ).stdout.strip()
        else:
            self.exampleInput = self.commandName
            self.exampleOutput = subprocess.run(
                [self.commandName], capture_output=True, text=True
            ).stdout.splitlines()

        # Getting the related commands for the command
        compOutput = subprocess.run(
            ["bash -c 'compgen -c'"], capture_output=True, text=True, shell=True
        )
        for output in compOutput.stdout.splitlines():
            if self.commandName in output:
                count += 1
                self.relatedCommands.append(output)
                if count == 3:
                    break

    def printManual(self):
        print(f"Command Name: {self.commandName}")
        print(f"Description: {self.description}")
        print(f"Version: {self.version}")
        if self.exampleOutput:
            print(f"Example Input: {self.exampleInput}")
            print(f"Example Output: {self.exampleOutput}")
        else:
            print(f"Example Input: {self.exampleInput}")
            print(f"Example Output: An error occurred")
        print("Related Commands:", ", ".join(self.relatedCommands))

    def setUpRecommendations(self):
        if self.commandName == "touch":
            self.recommendedCommands.append(["nano", "rm", "cat"])
        elif self.commandName == "echo":
            self.recommendedCommands.append(["printf", "cat", "grep"])
        elif self.commandName == "cat":
            self.recommendedCommands.append(["tail", "head", "grep", "nano"])
        elif self.commandName == "head":
            self.recommendedCommands.append(["touch", "tail", "cat"])
        elif self.commandName == "tail":
            self.recommendedCommands.append(["touch", "head", "cat"])
        elif self.commandName == "ls":
            self.recommendedCommands.append(["cd", "cat", "tree"])
        elif self.commandName == "users":
            self.recommendedCommands.append(["who", "w", "id"])
        elif self.commandName == "who":
            self.recommendedCommands.append(["users", "w", "last"])
        elif self.commandName == "pwd":
            self.recommendedCommands.append(["cd", "ls", "mkdir"])
        elif self.commandName == "date":
            self.recommendedCommands.append(["cal", "timedatectl", "hwclock"])
        elif self.commandName == "ps":
            self.recommendedCommands.append(["top", "kill", "htop"])
        elif self.commandName == "id":
            self.recommendedCommands.append(["groups", "whoami", "usermod"])
        elif self.commandName == "groups":
            self.recommendedCommands.append(["id", "groupadd", "usermod"])
        elif self.commandName == "du":
            self.recommendedCommands.append(["df", "ls", "find"])
        elif self.commandName == "grep":
            self.recommendedCommands.append(["awk", "sed", "find"])


class XmlSerializer:
    def __init__(self, manual):
        self.serializeOne(manual)
        self.serializeAll(manual)
        self.addCommandManual(manual)
        self.prettify(manual)

    def serializeOne(manual):
        # Similar to the serialize method, but for   a single CommandManual instance
        root = ET.Element("Manuals")
        XmlSerializer.addCommandManual(manual, root)
        return XmlSerializer.prettify(root)

    def serializeAll(manuals):
        root = ET.Element("Manuals")
        for manual in manuals:
            XmlSerializer.addCommandManual(manual, root)
        return XmlSerializer.prettify(root)

    def addCommandManual(manual, root):
        # Factor out the common logic for adding CommandManual elements to the XML root
        cmd_manual_element = ET.SubElement(root, "CommandManual")
        ET.SubElement(cmd_manual_element, "CommandName").text = manual.commandName
        ET.SubElement(
            cmd_manual_element, "CommandDescription"
        ).text = manual.description
        ET.SubElement(cmd_manual_element, "VersionHistory").text = manual.version
        ET.SubElement(
            cmd_manual_element, "Example"
        ).text = f"Input: {manual.exampleInput}, Output: {manual.exampleOutput}"
        ET.SubElement(cmd_manual_element, "RelatedCommands").text = ", ".join(
            manual.relatedCommands
        )

    def prettify(root):
        # Convert the ElementTree to a string and pretty-print
        rough_string = ET.tostring(root, "utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


class ManualGeneratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Command Manual Generator")

        # Configure the master window for responsiveness
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

        # Main frame that holds all other widgets and frames
        self.main_frame = ttk.Frame(master)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Initialize the commandManualGenerator attribute
        self.myManual = commandManualGenerator()

        # Setup frames
        self.firstRow()
        self.secondRow()
        self.thirdRow()
        self.fillComboBox()

    def firstRow(self):
        self.firstRow = ttk.Frame(self.main_frame)
        self.firstRow.grid(row=0, column=0, sticky="ew")
        self.firstRow.columnconfigure(5, weight=1)

        # Load Commands Button
        self.btnLoadCommands = ttk.Button(
            self.firstRow, text="Load Commands", command=self.loadCommands
        )
        self.btnLoadCommands.grid(row=0, column=0, padx=5, pady=5)

        # Create XML Files Button
        self.btnCreateXML = ttk.Button(
            self.firstRow,
            text="Generate All Manuals",
            command=self.createXMLFiles,
        )
        self.btnCreateXML.grid(row=0, column=1, padx=5, pady=5)

        # Print to Terminal Button
        self.btnPrintTerminal = ttk.Button(
            self.firstRow, text="Print to Terminal", command=self.printToTerminal
        )
        self.btnPrintTerminal.grid(row=0, column=2, padx=5, pady=5)

        # Delete XML Files Button
        self.btnDeleteXml = ttk.Button(
            self.firstRow, text="Delete XML Files", command=self.deleteXML
        )
        self.btnDeleteXml.grid(row=0, column=3, padx=5, pady=5)

        # Entry for single command XML creation
        self.singleCommandEntry = ttk.Entry(self.firstRow, width=40)
        self.singleCommandEntry.grid(row=0, column=4, padx=5, pady=5)
        self.singleCommandEntry.insert(0, "Enter command")

        # Create Command XML Button
        self.btnCreateSingleXML = ttk.Button(
            self.firstRow,
            text="Create Command XML",
            command=self.createSingleXML,
        )
        self.btnCreateSingleXML.grid(row=0, column=5, padx=5, pady=5)

    def secondRow(self):
        self.secondRow = ttk.Frame(self.main_frame)
        self.secondRow.grid(row=1, column=0, sticky="ew")
        self.secondRow.columnconfigure(1, weight=1)

        # Select Command Label
        self.lblCommand = ttk.Label(self.secondRow, text="Select Command:")
        self.lblCommand.grid(row=0, column=0, padx=5, pady=5)

        # Command ComboBox
        self.selectedCommand = tk.StringVar()
        self.commandCombo = ttk.Combobox(
            self.secondRow, textvariable=self.selectedCommand, state="readonly"
        )
        self.commandCombo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Generate Manual Button
        self.btnGenerateManual = ttk.Button(
            self.secondRow, text="Generate Manual", command=self.generateManual
        )
        self.btnGenerateManual.grid(row=0, column=2, padx=5, pady=5)

        # Open Manual Button
        self.btnOpenManual = ttk.Button(
            self.secondRow, text="Open Manual", command=self.openManual
        )
        self.btnOpenManual.grid(row=0, column=3, padx=5, pady=5)

        # Show Recommended Commands Button
        self.btnShowRecommendedCommands = ttk.Button(
            self.secondRow,
            text="Recommend Commands",
            command=self.recommendedCommands,
        )
        self.btnShowRecommendedCommands.grid(row=0, column=4, padx=5, pady=5)

    def thirdRow(self):
        self.thirdRow = ttk.Frame(self.main_frame)
        self.thirdRow.grid(row=2, column=0, sticky="nsew")
        self.thirdRow.rowconfigure(0, weight=1)
        self.thirdRow.columnconfigure(0, weight=1)

        # Manual ScrolledText
        self.manualText = scrolledtext.ScrolledText(self.thirdRow, width=80, height=20)
        self.manualText.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Run Command Entry
        self.runCommandEntry = ttk.Entry(self.thirdRow, width=125)
        self.runCommandEntry.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.runCommandEntry.insert(0, "Enter command")

        # Run Command Button
        self.btnRunCommand = ttk.Button(
            self.thirdRow, text="Run Command", command=self.runCommand
        )
        self.btnRunCommand.grid(row=1, column=0, padx=5, pady=5, sticky="nes")

        # Output for Run Command
        self.outputText = scrolledtext.ScrolledText(self.thirdRow, width=80, height=10)
        self.outputText.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

    def fillComboBox(self):
        # Extract command names from the manual objects to populate the Combobox
        commands = [manual.commandName for manual in self.myManual.manual]
        self.commandCombo["values"] = commands

        # Update the ComboBox with commands from the file
        self.commandCombo["values"] = commands

        if commands:
            self.commandCombo.current(0)

    def loadCommands(self):
        # Create an instance of commandManualGenerator with "commands.txt"
        self.myManual.readFile("commands.txt")
        self.fillComboBox()
        messagebox.showinfo("Success", "Commands were read from commands.txt.")

    def createXMLFiles(self):
        if self.myManual:
            self.myManual.createCommandsManuals()
            messagebox.showinfo(
                "Success", "Generated the manuals for the loaded commands."
            )
        else:
            messagebox.showerror("Error", "Please load the commands first.")

    def printToTerminal(self):
        if self.myManual:
            self.myManual.printManualsToTerminal()
        else:
            messagebox.showerror("Error", "Please load the commands first.")

    def deleteXML(self):
        for xml_file in glob.glob("*.xml"):
            os.remove(xml_file)

    def createSingleXML(self):
        commandName = self.singleCommandEntry.get()
        if commandName:
            # Check if the command already exists in the manual
            if not any(
                manual.commandName == commandName for manual in self.myManual.manual
            ):
                commandManual = CommandManual(commandName)
                self.myManual.addCommand(commandName)
                self.myManual.createCommandsManuals()  # Recreate the general XML file

                # Update the ComboBox values to include the new command
                self.fillComboBox()

                messagebox.showinfo(
                    "Success",
                    f"XML for '{commandName}' created and added to general XML.",
                )
            else:
                messagebox.showwarning(
                    "Warning", f"Command '{commandName}' already exists."
                )

    def generateManual(self):
        # This method should generate a manual for the selected command and provide feedback in the GUI
        selectedCommand = self.selectedCommand.get()
        if selectedCommand:
            self.myManual.addCommand(selectedCommand)
            self.myManual.createCommandsManuals()
            messagebox.showinfo("Success", f"Manual for '{selectedCommand}' generated.")

    def openManual(self):
        selectedCommand = self.selectedCommand.get()
        manualContent = ""
        if selectedCommand:
            file_path = f"{selectedCommand}.xml"  # Construct the file path
            if os.path.exists(file_path):  # Check if the file exists
                tree = ET.parse("manual.xml")
                root = tree.getroot()
                for commandManual in root.findall("CommandManual"):
                    commandName = commandManual.find("CommandName").text.strip()
                    if commandName == selectedCommand:
                        storedDescription = commandManual.find(
                            "CommandDescription"
                        ).text.strip()
                        storedVersion = commandManual.find(
                            "VersionHistory"
                        ).text.strip()
                        storedExample = commandManual.find("Example").text.strip()
                        storedExampleInput, storedExampleOutput = storedExample.split(
                            ",", 1
                        )
                        storedExampleInput = storedExampleInput.strip()
                        storedExampleOutput = storedExampleOutput.strip()
                        manualContent = (
                            "Name: "
                            + commandName
                            + "\n"
                            + "Description: "
                            + storedDescription
                            + "\n"
                            + "Version: "
                            + storedVersion
                            + "\n"
                            + "Example "
                            + storedExampleInput
                            + "\n"
                            + "Example "
                            + storedExampleOutput
                        )
                        self.manualText.delete("1.0", tk.END)
                        self.manualText.insert(tk.INSERT, manualContent)
            else:
                messagebox.showerror(
                    "Error", f"The manual for '{selectedCommand}' does not exist."
                )

    def recommendedCommands(self):
        selectedCommand = self.selectedCommand.get()
        if selectedCommand:
            for command in self.myManual.manual:
                if command.commandName == selectedCommand:
                    self.manualText.delete("1.0", tk.END)
                    self.manualText.insert(tk.INSERT, command.recommendedCommands)

    def runCommand(self):
        command = self.runCommandEntry.get()
        if command:
            try:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True
                )
                self.outputText.delete("1.0", tk.END)
                output = result.stdout if result.stdout else result.stderr
                self.outputText.insert(tk.INSERT, output)
            except subprocess.CalledProcessError as e:
                self.outputText.insert(tk.INSERT, f"An error occurred: {e}")


root = tk.Tk()
app = ManualGeneratorGUI(root)
root.mainloop()