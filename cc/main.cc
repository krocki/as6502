#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <string>
#include <vector>
#include <sstream>
#include <fstream>
#include <map>

void split(const std::string &s, const std::string delim, std::vector<std::string> &tokens) {

  auto start = 0U;
  auto end = s.find(delim);
  while (end != std::string::npos)
  {
    if (end-start>0) {
      tokens.push_back(s.substr(start, end-start));
    }
    start = end + delim.length();
    end = s.find(delim, start);
  }

  tokens.push_back(s.substr(start));
}

template <typename T>
void print_vector(std::vector<T> &v) {
  for (auto &t: v) {
    std::cout << "[" << t << "] ";
  }
  std::cout << "\n";
}

struct codeline {
  size_t line_no;
  std::string label;
  std::string code;
  std::string comment;
};

void print_codeline(struct codeline &l) {
  std::cout << std::right << std::setw(4) << l.line_no << " | " << std::left << std::setw(10) << l.label << std::left <<
    std::setw(25) << l.code << std::left << std::setw(25) << l.comment << "\n";
};

bool string_is_empty(std::string &str) {
  return (str.find_first_not_of(' ') == std::string::npos);
}

int main(int argc, char **argv) {

  if (argc < 2) {
    printf("usage: %s file\n", argv[0]);
    return -1;
  }

  printf("parsing %s\n", argv[1]);
  std::ifstream infile(argv[1]);
  std::ofstream dbg("debug.txt");

  std::string line;

  std::map<size_t, struct codeline> lines;

  // start with line no 1, not 0
  size_t line_no = 1;

  while (std::getline(infile, line)) {
    std::istringstream iss(line);

    std::string label = "";
    std::string comment = "";
    std::string text = "";
    std::string code = "";

    /* strip comments */
    auto end = line.find(";");
    if (end != std::string::npos) {
      text = line.substr(0, end);
      comment = line.substr(end);
    } else {
      text = line;
    }

    /* check if label */
    end = text.find(":");
    if (end != std::string::npos) {
      label = text.substr(0, end+1);
      code = text.substr(end+1);
    } else {
      code = text;
    }

    /* trim leading whitespace */
    end = code.find_first_not_of(' ');
    if (end == std::string::npos) {
      code = "";
    } else {
      code = code.substr(end);
    }

    if (!string_is_empty(code) or comment.length() > 0 or label.length() > 0) {
      dbg << std::right << std::setw(4) << line_no << " | " << std::left << std::setw(10) << label << std::left << std::setw(25) << code << std::left << std::setw(25) << comment << "\n";
      lines[line_no] = {line_no, label, code, comment};
    }

    line_no++;
  }

  std::cout << std::setw(4) << "LINE" << " | " << std::left << std::setw(10) << "LABEL" << std::left << std::setw(25) <<
    "CODE" << std::left << std::setw(25) << "COMMENT" << "\n";
  for (auto &c: lines) {
    print_codeline(c.second);
  };

  infile.close();
  dbg.close();
  return 0;
}

