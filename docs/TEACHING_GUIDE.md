# Kanji Time Teaching Guide - Quick Reference

**Companion to:** CODEBASE_REVIEW.md
**Audience:** Code-in-Place instructors and students
**Last Updated:** October 26, 2025

---

## Quick Navigation

### 🌟 Showcase Code (Study These!)

| Topic | File | Lines | What to Learn |
|-------|------|-------|---------------|
| **Protocol-based Design** | `visual/protocol/content.py` | 100-238 | PEP 544 protocols, interface design |
| **Immutable Value Types** | `visual/layout/distance.py` | 112-470 | namedtuple extension, operator overloading |
| **Template Method Pattern** | `kanji_time_cli.py` | 155-282 | Separation of concerns, plugin architecture |
| **State Machine** | `visual/protocol/content.py` | 48-98 | IntFlag enums, state transitions |
| **Descriptors** | `utilities/class_property.py` | 1-18 | Clean implementation, descriptor protocol |
| **Context Managers** | `utilities/general.py` | 29-78 | Resource management with `with` |

### ⚠️ Discussion Topics (What Would You Do Differently?)

| Issue | File | Lines | Discussion Question |
|-------|------|-------|---------------------|
| **Metaclass Caching** | `external_data/kanji_svg.py` | 75-117 | "When is a metaclass overkill? What's the alternative?" |
| **Match on Types** | `external_data/kanji_svg.py` | 622-634 | "Is this the right use of match? What's it for?" |
| **Utilities Dumping Ground** | `utilities/general.py` | All | "How should this module be organized?" |
| **Custom Dict Immutability** | `utilities/general.py` | 80-128 | "What does stdlib provide? (hint: MappingProxyType)" |

### ❌ Fix Before Showing

| Issue | File | Lines | Why Fix? |
|-------|------|-------|----------|
| **"OMFG..." comment** | `external_data/kanji_svg.py` | 494 | Unprofessional, discourages type hints |
| **"deleted by GPT"** | `external_data/kanji_svg.py` | 443-454 | Poor version control hygiene |
| **Magic exit codes** | `kanji_time_cli.py` | 369,379,384,388 | Should use named constants |
| **Duplicate import** | `kanji_time_cli.py` | 81-82 | Sloppy coding |
| **Typo in docstring** | `svg_transform.py` | 1-5 | "he" → "The", remove "Pshaw" |

---

## Teaching Session Plans

### Session 1: Protocol-Based Architecture (90 min)

**Learning Goals:**
- Understand PEP 544 runtime-checkable protocols
- See how protocols enable plugin systems
- Learn separation of interface from implementation

**Code to Review:**
1. `visual/protocol/content.py` - The `RenderingFrame` protocol
2. `kanji_time_cli.py:155-282` - How CLI uses protocols
3. `reports/practice_sheet/report.py` - Plugin implementation

**Activities:**
1. Trace the execution flow from CLI through protocol
2. Design a new report plugin (on paper)
3. Discuss: "Why protocols instead of abstract base classes?"

**Homework:**
Implement a simple "Kanji Flashcard" report plugin

---

### Session 2: Immutable Value Types (90 min)

**Learning Goals:**
- Understand immutability benefits
- Learn namedtuple extension pattern
- Explore operator overloading

**Code to Review:**
1. `visual/layout/distance.py:112-470` - The Distance class
2. `visual/layout/region.py` - Extent, Pos, Region types
3. Test file: `visual/layout/test/test_distance.py`

**Activities:**
1. Create simple value type (Temperature with Celsius/Fahrenheit)
2. Add operator overloading (+, -, *, /)
3. Discuss: "Why immutability? What are the tradeoffs?"

**Demonstration:**
Show bug that immutability prevents:
```python
# Mutable - accidental modification
point = [0, 0]
def move(p): p[0] += 10  # Oops, modified shared state!

# Immutable - safe
Point = namedtuple('Point', 'x y')
point = Point(0, 0)
def move(p): return Point(p.x + 10, p.y)  # Returns new instance
```

---

### Session 3: Design Patterns in the Wild (90 min)

**Learning Goals:**
- Identify Gang of Four patterns in real code
- Understand when to use each pattern
- Learn pattern trade-offs

**Patterns Found in Kanji Time:**

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Template Method** | `kanji_time_cli.py:155-282` | Define algorithm skeleton |
| **Strategy** | `visual/layout/stack_layout.py` | Layout algorithms |
| **Singleton** | `utilities/singleton.py` | One instance only |
| **Adapter** | `adapter/svg.py` | Convert between interfaces |
| **Factory** | `external_data/kanji_svg.py:61-72` | Create objects |

**Activities:**
1. Draw sequence diagrams for Template Method
2. Identify where Strategy could replace if/elif chains
3. Discuss: "Are patterns being used correctly here?"

---

### Session 4: Technical Debt - What & Why (90 min)

**Learning Goals:**
- Recognize different types of technical debt
- Understand intentional vs accidental debt
- Learn when to pay down debt

**Code to Review:**
1. `external_data/kanji_svg.py` - The "dirty" file
2. `utilities/general.py` - The dumping ground
3. `kanji_time_cli.py` - Magic numbers

**Activities:**
1. Categorize debt: "Ship it", "Fix soon", "Fix now", "Never ship"
2. Refactoring exercise: Split kanji_svg.py
3. Estimate: How long to pay down each debt item?

**Discussion Questions:**
- "Why did the developer ship code with 'deleted by GPT' markers?"
- "When is 'good enough' actually good enough?"
- "How do you decide what debt to tackle first?"

---

### Session 5: Testing Real Code (90 min)

**Learning Goals:**
- Read real test suites
- Identify coverage gaps
- Write tests for complex code

**Code to Review:**
1. `visual/layout/test/test_distance.py` - Well-written tests
2. `external_data/kanji_svg.py` - NO TESTS (why?)
3. Test structure and organization

**Activities:**
1. Run pytest and examine output
2. Identify: "What's not tested in kanji_svg.py?"
3. Write tests for one function in kanji_svg.py

**Coverage Exercise:**
```bash
pytest --cov=kanji_time --cov-report=html
# Open htmlcov/index.html
# Find the red (untested) lines
```

---

## Student Exercises

### Beginner Level

**Exercise 1: Fix the Easy Stuff**
1. Remove duplicate import in `kanji_time_cli.py:81-82`
2. Add named constants for exit codes
3. Fix typo in `svg_transform.py` docstring
4. Remove "OMFG" comment from `kanji_svg.py:494`

**Exercise 2: Organize Utilities**
1. Read `utilities/general.py`
2. Group functions by purpose
3. Propose new file structure
4. Create one new organized module

### Intermediate Level

**Exercise 3: Replace Custom Code with Stdlib**
1. Replace `flatten()` with `itertools.chain.from_iterable`
2. Replace `no_dict_mutators()` with `MappingProxyType`
3. Write tests confirming equivalence
4. Measure performance difference

**Exercise 4: Add Type Hints**
1. Choose one module missing type hints
2. Add complete type annotations
3. Run `mypy` to validate
4. Fix any type errors revealed

**Exercise 5: Improve Error Handling**
1. Create `kanji_time/exceptions.py` with custom exceptions
2. Replace assertions in public APIs with exceptions
3. Add error handling tests
4. Document error conditions

### Advanced Level

**Exercise 6: Refactor kanji_svg.py**
1. Split into `loader.py`, `renderer.py`, `cache.py`
2. Replace metaclass with `@lru_cache`
3. Extract XML utilities
4. Maintain backward compatibility
5. Add comprehensive tests

**Exercise 7: Create a New Report Plugin**
1. Design a "Kanji Quiz" report (multiple choice)
2. Implement using `RenderingFrame` protocol
3. Add to `VALID_REPORTS` registry
4. Write integration tests
5. Document the report

**Exercise 8: Add CLI Integration Tests**
1. Use pytest fixtures and subprocess
2. Test invalid inputs, missing files, etc.
3. Test report generation end-to-end
4. Aim for 80% CLI coverage

---

## Code Reading Checklist

When reviewing a new module, ask:

### Architecture
- [ ] What's this module's single responsibility?
- [ ] What are its dependencies? Are they appropriate?
- [ ] How does it fit in the overall system?
- [ ] What design patterns are used?

### Code Quality
- [ ] Are there type hints on public APIs?
- [ ] Is error handling consistent?
- [ ] Are variable names clear?
- [ ] Is there dead/commented code?
- [ ] Are there "TODO" or "FIXME" comments?

### Testing
- [ ] Is there a corresponding test file?
- [ ] What's tested? What's not?
- [ ] Are tests readable?
- [ ] Do tests have good names?

### Documentation
- [ ] Are docstrings present?
- [ ] Do docstrings explain *why*, not just *what*?
- [ ] Is there inline documentation for complex logic?
- [ ] Are there examples?

---

## Common Student Questions

### "Why use protocols instead of inheritance?"

**Short Answer:** Protocols allow structural typing (duck typing with type checking) without coupling.

**Example:**
```python
# Inheritance - tight coupling
class ReportBase(ABC):
    @abstractmethod
    def draw(self): ...

class MyReport(ReportBase):  # Must inherit
    def draw(self): ...

# Protocol - loose coupling
class RenderingFrame(Protocol):
    def draw(self): ...

class MyReport:  # No inheritance needed!
    def draw(self): ...  # Just implement the interface
```

**Benefits:**
- No inheritance hierarchy
- Can work with third-party classes
- Multiple protocols without multiple inheritance
- Runtime checking with `isinstance(obj, Protocol)`

---

### "Why is kanji_svg.py so complex?"

**Answer:** Evolution from Jupyter notebook to production code.

**Timeline:**
1. Started in Jupyter - quick prototype
2. Added features organically
3. Never refactored into clean modules
4. Ships working code but has technical debt

**Lessons:**
- Notebooks → production requires refactoring
- "Working" ≠ "well-designed"
- Refactoring is normal and necessary
- Complexity accumulates without discipline

---

### "Should I use match statements for type checking?"

**Short Answer:** No. Use match for *structural* patterns, not `isinstance()`.

**Bad (current code):**
```python
match stroke_range:
    case x if isinstance(x, int):  # This is just isinstance!
        ...
    case x if isinstance(x, list):
        ...
```

**Good - isinstance directly:**
```python
if isinstance(stroke_range, int):
    ...
elif isinstance(stroke_range, list):
    ...
```

**Good - structural match:**
```python
match point:
    case (0, 0):  # Origin
        ...
    case (x, 0):  # On x-axis
        ...
    case (0, y):  # On y-axis
        ...
```

---

### "When should I use a metaclass?"

**Short Answer:** Almost never. There's usually a simpler way.

**Use metaclasses for:**
- Enforcing subclass contracts (like Django models)
- Automatic registration of classes
- Modifying class creation behavior

**Don't use metaclasses for:**
- ❌ Caching (use `@lru_cache`)
- ❌ Singletons (use module-level instance)
- ❌ Validation (use `__init_subclass__`)

**Rule of thumb:** If you're not sure you need a metaclass, you don't.

---

### "How do I know when code is 'good enough' to ship?"

**Framework:**

**Must have:**
- ✅ Solves the user's problem
- ✅ No known security issues
- ✅ No data-loss bugs
- ✅ Core functionality tested

**Should have:**
- ⚠️ Good error messages
- ⚠️ Reasonable performance
- ⚠️ Basic documentation
- ⚠️ Some test coverage

**Nice to have:**
- 💚 Beautiful code
- 💚 100% test coverage
- 💚 Perfect documentation
- 💚 Optimal performance

**Kanji Time shipped with:**
- All "must haves" ✅
- Most "should haves" ⚠️
- Some "nice to haves" (good architecture, some beautiful code)

**The lesson:** Perfect is the enemy of shipped. Ship when "must haves" are done and document the debt.

---

## Quick Reference: Where is the Code?

### By Topic

**Plugin System:**
- Protocol definition: `visual/protocol/content.py`
- CLI loader: `kanji_time_cli.py:117-153` (load_report_module)
- Report registry: `kanji_time_cli.py:89-92` (VALID_REPORTS)
- Example plugin: `reports/practice_sheet/report.py`

**Geometry System:**
- Distance: `visual/layout/distance.py`
- Position: `visual/layout/region.py` (Pos class)
- Extent: `visual/layout/region.py` (Extent class)
- Region: `visual/layout/region.py` (Region class)

**Data Loading:**
- SVG loading: `external_data/kanji_svg.py:498-573`
- Kanji dictionary: `external_data/kanji_dic2.py`
- Radicals: `external_data/radicals.py`

**Rendering:**
- PDF surface: `utilities/general.py:68-78` (pdf_canvas)
- ReportLab init: `kanji_time_cli.py:98-115`
- Drawing frames: `visual/frame/` (entire module)

---

## Additional Resources

### External Reading

**Python Patterns:**
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [Gang of Four Patterns in Python](https://github.com/faif/python-patterns)
- [Real Python - Immutability](https://realpython.com/python-immutability/)

**Testing:**
- [pytest documentation](https://docs.pytest.org/)
- [Test-Driven Development by Example (Kent Beck)](https://www.amazon.com/dp/0321146530)

**Refactoring:**
- [Refactoring: Improving the Design of Existing Code (Martin Fowler)](https://martinfowler.com/books/refactoring.html)
- [Working Effectively with Legacy Code (Michael Feathers)](https://www.amazon.com/dp/0131177052)

### In This Repository

- **Full Review:** `docs/CODEBASE_REVIEW.md`
- **README:** `README.md`
- **Contributing:** (TODO - create this!)
- **Architecture Docs:** `docs/source/design/`

---

## Feedback & Questions

This teaching guide is a living document. Suggestions for improvement welcome!

**Maintainer:** Andrew Milton (HouseElves)
**Contributors:** Claude (Anthropic) - Initial analysis and review

---

*"Code doesn't need to be perfect to ship—but one does need to be smart about what imperfections to ship and have a plan to correct them."* — Kanji Time README.md
