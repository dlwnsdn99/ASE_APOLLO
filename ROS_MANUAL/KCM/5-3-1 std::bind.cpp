#include <algorithm>
#include <functional>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

class Object {
public:
  void greeting(const string &str) { cout << "Hello, " << str << endl; }
};

void good_bye(const string &str) { cout << str << endl; }

int main() {
  Object my_obj;

	//여기!
  auto obj_greeting =
      std::bind(&Object::greeting, &my_obj, std::placeholders::_1);

  obj_greeting("Swimming Kim");

  return 0;
}

