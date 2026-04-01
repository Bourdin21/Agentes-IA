using BlankProject.Domain.Entities;

namespace BlankProject.Application.Interfaces;

/// <summary>
/// Interfaz base para repositorios genéricos.
/// </summary>
public interface IRepository<T> where T : SoftDestroyable
{
    Task<T?> GetByIdAsync(int id);
    Task<List<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(T entity);
    Task SaveChangesAsync();
}
