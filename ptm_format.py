import re


def splitfullname(fullname):
    firstname = ""
    lastname = ""
    suffix = ""
    fullname = fullname.strip().upper()
    vCountSpaces = fullname.count(" ")
    if vCountSpaces == 0:
        lastname = fullname
    elif vCountSpaces == 1:
        firstname = fullname.partition(" ")[0]
        lastname = fullname.partition(" ")[2]
    else:
        # Repmove any prefixes
        if fullname.startswith("DR. "):
            fullname = fullname.replace("DR. ", "")
        elif fullname.startswith("DR "):
            fullname = fullname.replace("DR ", "")
        elif fullname.startswith("DRE "):
            fullname = fullname.replace("DRE ", "")
        elif fullname.startswith("MR. "):
            fullname = fullname.replace("MR. ", "")
        elif fullname.startswith("MR "):
            fullname = fullname.replace("MR ", "")
        elif fullname.startswith("MRS. "):
            fullname = fullname.replace("MRS. ", "")
        elif fullname.startswith("MRS "):
            fullname = fullname.replace("MRS ", "")
        elif fullname.startswith("MISS "):
            fullname = fullname.replace("MISS ", "")
        elif fullname.startswith("MS. "):
            fullname = fullname.replace("MS. ", "")
        elif fullname.startswith("MS "):
            fullname = fullname.replace("MS ", "")
        elif fullname.startswith("MME. "):
            fullname = fullname.replace("MME. ", "")
        elif fullname.startswith("MME "):
            fullname = fullname.replace("MME ", "")
        # First remove any suffixes
        if fullname.endswith(" JR"):
            suffix = "JR"
            fullname = fullname[:-3]
        elif fullname.endswith(" JUNIOR"):
            suffix = "JUNIOR"
            fullname = fullname[:-7]
        elif fullname.endswith(" III"):
            suffix = "III"
            fullname = fullname[:-4]
        elif fullname.endswith(" II"):
            suffix = "II"
            fullname = fullname[:-3]
        elif fullname.endswith(" IV"):
            suffix = "IV"
            fullname = fullname[:-3]
        elif fullname.endswith(" SR"):
            suffix = "SR"
            fullname = fullname[:-3]
            # Now handle any multi word last names
        if ")" in fullname:
            lastname = fullname.partition(")")[2]
            firstname = fullname.partition(")")[0] + fullname.partition(")")[1]
        elif " VAN " in fullname:
            lastname = fullname.partition(" VAN ")[1] + fullname.partition(" VAN ")[2]
            firstname = fullname.partition(" VAN ")[0]
        elif " DER " in fullname:
            lastname = fullname.partition(" DER ")[1] + fullname.partition(" DER ")[2]
            firstname = fullname.partition(" DER ")[0]
        elif " VANDER " in fullname:
            lastname = (
                fullname.partition(" VANDER ")[1] + fullname.partition(" VANDER ")[2]
            )
            firstname = fullname.partition(" VANDER ")[0]
        elif " DE " in fullname:
            lastname = fullname.partition(" DE ")[1] + fullname.partition(" DE ")[2]
            firstname = fullname.partition(" DE ")[0]
        elif " ABD " in fullname:
            lastname = fullname.partition(" ABD ")[1] + fullname.partition(" ABD ")[2]
            firstname = fullname.partition(" ABD ")[0]
        elif " EL " in fullname:
            lastname = fullname.partition(" EL ")[1] + fullname.partition(" EL ")[2]
            firstname = fullname.partition(" EL ")[0]
        elif " DEL " in fullname:
            lastname = fullname.partition(" DEL ")[1] + fullname.partition(" DEL ")[2]
            firstname = fullname.partition(" DEL ")[0]
        elif " DELA " in fullname:
            lastname = fullname.partition(" DELA ")[1] + fullname.partition(" DELA ")[2]
            firstname = fullname.partition(" DELA ")[0]
        elif " DELLA " in fullname:
            lastname = (
                fullname.partition(" DELLA ")[1] + fullname.partition(" DELLA ")[2]
            )
            firstname = fullname.partition(" DELLA ")[0]
        elif " DI " in fullname:
            lastname = fullname.partition(" DI ")[1] + fullname.partition(" DI ")[2]
            firstname = fullname.partition(" DI ")[0]
        elif " DOS " in fullname:
            lastname = fullname.partition(" DOS ")[1] + fullname.partition(" DOS ")[2]
            firstname = fullname.partition(" DOS ")[0]
        elif " DU " in fullname:
            lastname = fullname.partition(" DU ")[1] + fullname.partition(" DU ")[2]
            firstname = fullname.partition(" DU ")[0]
        elif " LE " in fullname:
            lastname = fullname.partition(" LE ")[1] + fullname.partition(" LE ")[2]
            firstname = fullname.partition(" LE ")[0]
        elif " ST " in fullname:
            lastname = fullname.partition(" ST ")[1] + fullname.partition(" ST ")[2]
            firstname = fullname.partition(" ST ")[0]
        elif " ST. " in fullname:
            lastname = fullname.partition(" ST. ")[1] + fullname.partition(" ST. ")[2]
            firstname = fullname.partition(" ST. ")[0]
        elif " VON " in fullname:
            lastname = fullname.partition(" VON ")[1] + fullname.partition(" VON ")[2]
            firstname = fullname.partition(" VON ")[0]
        elif " DER " in fullname:
            lastname = fullname.partition(" DER ")[1] + fullname.partition(" DER ")[2]
            firstname = fullname.partition(" DER ")[0]
        else:
            firstname = fullname.rpartition(" ")[0]
            lastname = fullname.rpartition(" ")[2]
    # remove any leading or trailing spaces
    firstname = firstname.strip()
    lastname = lastname.strip()
    return firstname, lastname, suffix


def fit_phone(Phone):
    Phone = re.sub(r"^\+\s*1\s*", "", Phone)
    Phone = re.sub(r"^1[\s\-]*\(", "(", Phone)
    Phone = re.sub(r"^1[\s\-]*", "", Phone)

    # Handle additional occurrences of +1 or 1 in the middle of the string
    Phone = re.sub(r";\s*\+\s*1\s*", ";", Phone)
    Phone = re.sub(r";\s*1\s*", ";", Phone)

    pattern = r"[^0-9;]"
    phone_digits = re.sub(pattern, "", Phone)
    return phone_digits


# firstname, lastname, suffix = splitfullname("TAMMY E WILCOX-KRAUSHAAR")
# print(firstname)
# print(lastname)
# print(suffix)
