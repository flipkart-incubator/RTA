def domain_list(file_path):
    f = open(file_path, "r")
    lines = f.readlines()

    domains = []
    for line in lines:
        domains.append(line.strip())
    print(domains)
    return domains

def file_to_int_list(file_path):
    f = open(file_path, "r")
    lines = f.readlines()

    ans = []
    for line in lines:
        ans.append(int(line.strip()))
    return ans