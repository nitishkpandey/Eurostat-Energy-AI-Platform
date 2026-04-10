export const safeArray = (value) => (Array.isArray(value) ? value : []);

export const asNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

export const getTail = (arr) => (arr.length ? arr[arr.length - 1] : null);

export const isTextEntryElement = (target) => {
  if (!(target instanceof HTMLElement)) {
    return false;
  }

  const tag = target.tagName?.toLowerCase();
  return (
    tag === "input" ||
    tag === "textarea" ||
    tag === "select" ||
    target.isContentEditable ||
    target.closest("[contenteditable='true']") !== null
  );
};
