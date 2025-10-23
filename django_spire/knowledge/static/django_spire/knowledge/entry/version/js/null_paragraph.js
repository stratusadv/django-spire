class NullParagraph {
    static isReadOnlySupported = true;

    constructor({data, api, config, readOnly, block}){}

    render()
    {
        return null;
    }

    save()
    {
        return null;
    }
}