const { filterBooks } = require('./funcfilterUtils');

const mockBooks = [
    { Title: "#Girlboss", Author: "Sophia Amoruso", Genre: "Humor", ISBN: "9781591847939", Year: "2014", "In Stock": "yes", "Who Checked": "" },
    { Title: "Wildblood", Author: "Lauren Blackwood", Genre: "Fiction", ISBN: "9745671371823", Year: "1988", "In Stock": "no", "Who Checked": "User1" },
    { Title: "The Great Gatsby", Author: "Scott Fitzgerald", Genre: "Fiction", ISBN: "9783257691078", Year: "1925", "In Stock": "yes", "Who Checked": "" }
];

//***Functionality Test Case***

test('filters by title keyword', () => {
    const result = filterBooks(mockBooks, { searchText: "#Girlboss", sortBy: "", availability: "all", genre: "all", year: "" });
    expect(result.length).toBe(1);
    expect(result[0].Title).toBe("#Girlboss");
});

test('filters by author keyword', () => {
    const result = filterBooks(mockBooks, { searchText: "Blackwood", sortBy: "", availability: "all", genre: "all", year: "" });
    expect(result.length).toBe(1);
    expect(result[0].Author).toBe("Lauren Blackwood");
});

test('filters by availability', () => {
    const result = filterBooks(mockBooks, { searchText: "", sortBy: "", availability: "in", genre: "all", year: "" });
    expect(result.every(book => book["In Stock"] === "yes")).toBe(true);
});

test('filters by genre', () => {
    const result = filterBooks(mockBooks, { searchText: "", sortBy: "", availability: "all", genre: "Fiction", year: "" });
    expect(result.length).toBe(2);
});

test('filters by year', () => {
    const result = filterBooks(mockBooks, { searchText: "", sortBy: "", availability: "all", genre: "all", year: "1988" });
    expect(result.length).toBe(1);
    expect(result[0].Title).toBe("Wildblood");
});

test('applies multiple filters together', () => {
    const result = filterBooks(mockBooks, { searchText: "Great", sortBy: "", availability: "in", genre: "Fiction", year: "1925" });
    expect(result.length).toBe(1);
    expect(result[0].Title).toBe("The Great Gatsby");
});

//***Boundary Test Case***

test('input longer than 255 characters is ignored or truncated', () => {
    const longInput = 'a'.repeat(300);
    const result = filterBooks(mockBooks, {
        searchText: longInput,
        sortBy: "",
        availability: "all",
        genre: "all",
        year: ""
    });
    expect(result.length).toBe(0);
});

//***Error Handling Test Case***

test('handles special characters in search input', () => {
    const specialCharInput = "@#$%^&*()!";
    const result = filterBooks(mockBooks, {
        searchText: specialCharInput,
        sortBy: "",
        availability: "all",
        genre: "all",
        year: ""
    });
    // Expect no matches returned if the input is only special characters
    expect(result.length).toBe(0);
});
