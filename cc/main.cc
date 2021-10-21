#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <string>
#include <vector>
#include <sstream>
#include <fstream>
#include <regex>
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
  std::string op;
  std::string arg;
  std::string code;
  std::string comment;
};

void print_codeline(struct codeline &l) {
  std::cout << std::right << std::setw(4) << l.line_no << " | " << std::left << std::setw(10) << l.label << std::left <<
    std::setw(10) << l.op << std::left << std::setw(10) << l.arg << std::left << std::setw(25) << l.code << std::left << std::setw(25) << l.comment << "\n";
};

bool string_is_empty(std::string &str) {
  return (str.find_first_not_of(' ') == std::string::npos);
}

std::regex
line_expr(
    "^" // sol
    "\\s*((([A-Za-z0-9]+):)?" // label
    "\\s*(([a-zA-z]{3})" // op
    "(\\s+(.*?))?)?)?" // arg
    "(;.*)?" // comment
    "$"); // eol

struct codeline parse_regex(std::string &line) {

  std::match_results<std::string::const_iterator > mr;
  std::regex_search( line, mr, line_expr );
  std::cout << "line = " << line << " | " << mr.size() << " matches\n";

  for( std::size_t index = 0; index < mr.size(); ++index ){
    std::cout << index << " -> " << mr[ index ] << "\n";
  }

  //mr[0] - entire match (lhs + comment)
  //mr[1] - match lhs
  //mr[2] - label + ":"
  //mr[3] - label
  //mr[4] - whole instruction
  //mr[5] - instruction without operand
  //mr[6] - operand untrimmed
  //mr[7] - operand trimmed
  //mr[8] - comment (rhs)

  struct codeline cl{0, mr[3], mr[5], mr[7], mr[4], mr[8]};
  return cl;
}

struct codeline parse_split(std::string &line) {

  std::string text, comment, label, code;

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

  return {0, label, "", "", code, comment};
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
  std::map<std::string, size_t> labels;

  // start with line no 1, not 0
  size_t line_no = 1;

  while (std::getline(infile, line)) {
    std::istringstream iss(line);

    //auto [_, label, code, comment] = parse_split(line);
    auto [_, label, op, arg, code, comment] = parse_regex(line);

    if (label.length() > 0) {
      if (labels.find(label) != labels.end()) {
        printf("ERROR! label %s from line %zu redefined (line %zu)\n",
          label.c_str(), labels[label], line_no);
      }
      labels[label] = line_no;
    }

    if (!string_is_empty(code) or comment.length() > 0 or label.length() > 0) {
      dbg << std::right << std::setw(4) << line_no << " | " << std::left << std::setw(10) << label << std::left <<
        std::setw(10) << op << std::left << std::setw(10) << arg << std::left << std::setw(25) << code << std::left << std::setw(25) << comment << "\n";
      lines[line_no] = {line_no, label, op, arg, code, comment};
    }

    line_no++;
  }

  std::cout << std::setw(4) << "LINE" << " | " << std::left << std::setw(10) << "LABEL" << std::left << std::setw(10) <<
    "OP" << std::left << std::setw(10) << "ARG" << std::left << std::setw(25) << "CODE" << std::left << std::setw(25) << "COMMENT" << "\n";

  for (auto &c: lines) {
    print_codeline(c.second);
  };

  std::cout << "\nlabels: \n";
  for (auto &c: labels) {
    std::cout << c.first << "@" << c.second << "\n";
  }

  // Pass 1 - Find All Defines and Labels
  // Pass 2 - Assign PC and Pick Opcodes
  // Pass 3 - Transform Labels
  // Pass 4 - Resolve Label References

  infile.close();
  dbg.close();
  return 0;
}

