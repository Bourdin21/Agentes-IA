using BlankProject.Application.Interfaces;
using BlankProject.Domain.Entities;
using BlankProject.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BlankProject.Infrastructure.Repositories;

/// <summary>
/// Implementacion generica de repositorio con soft delete.
/// El query filter global en DbContext excluye registros con DeletedAt != null.
/// </summary>
public class Repository<T> : IRepository<T> where T : SoftDestroyable
{
    protected readonly AppDbContext _context;
    protected readonly DbSet<T> _dbSet;

    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }

    public virtual async Task<T?> GetByIdAsync(int id)
    {
        return await _dbSet.FindAsync(id);
    }

    public virtual async Task<List<T>> GetAllAsync()
    {
        return await _dbSet.ToListAsync();
    }

    public virtual async Task<T> AddAsync(T entity)
    {
        await _dbSet.AddAsync(entity);
        return entity;
    }

    public virtual async Task UpdateAsync(T entity)
    {
        _dbSet.Update(entity);
        await Task.CompletedTask;
    }

    /// <summary>
    /// Soft delete: marca la entidad como eliminada sin borrarla de la DB.
    /// </summary>
    public virtual async Task DeleteAsync(T entity)
    {
        entity.DeletedAt = DateTime.UtcNow;
        _dbSet.Update(entity);
        await Task.CompletedTask;
    }

    public virtual async Task SaveChangesAsync()
    {
        await _context.SaveChangesAsync();
    }
}
