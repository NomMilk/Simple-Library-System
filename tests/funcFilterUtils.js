function filterBooks(books, { searchText, sortBy, availability, genre, year }) {
    return books.filter(book => {
        const text = searchText.toLowerCase();
        let visible = true;

        // Search
        if (sortBy !== "") {
            const value = book[sortBy]?.toLowerCase() || "";
            if (!value.includes(text)) visible = false;
        } else {
            const title = book.Title.toLowerCase();
            const author = book.Author.toLowerCase();
            if (!(title.includes(text) || author.includes(text))) visible = false;
        }

        // Availability
        if (availability === "in" && book["In Stock"].toLowerCase() !== "yes") visible = false;
        if (availability === "out" && book["In Stock"].toLowerCase() === "yes") visible = false;

        // Genre
        if (genre !== "all" && book.Genre !== genre) visible = false;

        // Year
        if (year && parseInt(book.Year) !== parseInt(year)) visible = false;

        return visible;
    });
}
module.exports = { filterBooks };